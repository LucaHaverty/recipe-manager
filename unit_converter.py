import json
import os
from functools import lru_cache
from typing import Union, Dict, Any, List, Optional

class UnitConverter:
    """
    A static-like class for converting between different units of measurement.
    All methods can be called directly without instantiation.
    """
    
    _conversion_factors = None
    _default_conversion_file = os.path.join(os.path.dirname(__file__), 'conversions.json')
    
    @classmethod
    @lru_cache(maxsize=1)
    def _get_conversion_factors(cls, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load and cache conversion factors from a JSON file.
        
        Args:
            file_path (str, optional): Path to the JSON file containing conversion factors.
                If None, will use the default conversions.json file.
        
        Returns:
            dict: Dictionary of conversion factors.
        """
        if cls._conversion_factors is not None:
            return cls._conversion_factors
            
        if file_path is None:
            file_path = cls._default_conversion_file
            
        try:
            with open(file_path, 'r') as f:
                cls._conversion_factors = json.load(f)
                return cls._conversion_factors
        except FileNotFoundError:
            raise FileNotFoundError(f"Conversion file not found: {file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in conversion file: {file_path}")
    
    @classmethod
    def set_conversion_file(cls, file_path: str) -> None:
        """
        Set a custom conversion file to use for all future conversions.
        
        Args:
            file_path (str): Path to the JSON file containing conversion factors.
        """
        # Clear the cache and load the new file
        cls._get_conversion_factors.cache_clear()
        cls._conversion_factors = None
        # Force load to validate the file
        cls._get_conversion_factors(file_path)
        # Update default path
        cls._default_conversion_file = file_path
    
    @classmethod
    def convert(cls, value: Union[int, float], from_unit: str, to_unit: str, 
                conversion_file: Optional[str] = None) -> float:
        """
        Convert a value from one unit to another.
        
        Args:
            value (float or int): The value to convert.
            from_unit (str): The unit to convert from.
            to_unit (str): The unit to convert to.
            conversion_file (str, optional): Path to a custom conversion file to use just for this conversion.
            
        Returns:
            float: The converted value.
            
        Raises:
            ValueError: If the conversion is not possible.
        """
        # Get conversion factors (cached if using default file)
        factors = cls._get_conversion_factors(conversion_file)
        
        # If units are the same, no conversion needed
        if from_unit == to_unit:
            return float(value)
        
        # Direct conversion
        if from_unit in factors and to_unit in factors[from_unit]:
            return value * factors[from_unit][to_unit]
        
        # Check if reverse conversion exists
        if to_unit in factors and from_unit in factors[to_unit]:
            return value / factors[to_unit][from_unit]
        
        # Try to find a path between units using a recursive approach
        def find_conversion_path(current_unit, target_unit, visited=None):
            if visited is None:
                visited = set()
            
            visited.add(current_unit)
            
            # Check direct conversion
            if current_unit in factors and target_unit in factors[current_unit]:
                return [(current_unit, target_unit, factors[current_unit][target_unit])]
                
            # Try all possible intermediate units
            for intermediate_unit in factors.get(current_unit, {}):
                if intermediate_unit not in visited:
                    path = find_conversion_path(intermediate_unit, target_unit, visited)
                    if path:
                        return [(current_unit, intermediate_unit, factors[current_unit][intermediate_unit])] + path
                        
            return None
        
        path = find_conversion_path(from_unit, to_unit)
        if path:
            result = value
            for start_unit, end_unit, factor in path:
                result *= factor
            return result
            
        raise ValueError(f"No conversion path found from '{from_unit}' to '{to_unit}'")
    
    @classmethod
    def get_available_units(cls, conversion_file: Optional[str] = None) -> List[str]:
        """
        Get a list of all available units.
        
        Args:
            conversion_file (str, optional): Path to a custom conversion file.
            
        Returns:
            list: List of unit names.
        """
        factors = cls._get_conversion_factors(conversion_file)
        return list(factors.keys())
    
    @classmethod
    def get_compatible_units(cls, unit: str, conversion_file: Optional[str] = None) -> List[str]:
        """
        Get a list of units that can be directly converted to/from the given unit.
        
        Args:
            unit (str): The unit to find compatible units for.
            conversion_file (str, optional): Path to a custom conversion file.
            
        Returns:
            list: List of compatible unit names.
        """
        factors = cls._get_conversion_factors(conversion_file)
        compatible = set()
        
        # Units we can convert to
        if unit in factors:
            compatible.update(factors[unit].keys())
        
        # Units that can convert to this unit
        for other_unit, conversions in factors.items():
            if unit in conversions:
                compatible.add(other_unit)
        
        return list(compatible)