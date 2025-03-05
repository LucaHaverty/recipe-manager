import os
import json
import textwrap
from typing import Dict, List, Any, Optional

from unit_converter import UnitConverter
d
class RecipeManager:
    def __init__(self, data_file: str = "recipes.json", price_file: str = "ingredients.json"):
        self.data_file = data_file
        self.price_file = price_file
        self.recipes = self.load_recipes()
        self.price_data = self.load_price_data()
        self.current_path = []
        
    def load_price_data(self) -> Dict:
        """Load ingredient price data from JSON file."""
        if os.path.exists(self.price_file):
            try:
                with open(self.price_file, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print(f"Error reading {self.price_file}, creating empty price database.")
                return {}
        else:
            print(f"Price file {self.price_file} not found, creating empty price database.")
            return {}
    
    def save_price_data(self) -> None:
        """Save ingredient price data to JSON file."""
        with open(self.price_file, 'w') as file:
            json.dump(self.price_data, file, indent=2)
        print(f"Price data saved to {self.price_file}")
    
    def load_recipes(self) -> Dict:
        """Load recipes from JSON file or create a new structure."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print(f"Error reading {self.data_file}, creating new recipe database.")
                return {"folders": {}, "recipes": {}}
        else:
            return {"folders": {}, "recipes": {}}
    
    def save_recipes(self) -> None:
        """Save recipes to JSON file."""
        with open(self.data_file, 'w') as file:
            json.dump(self.recipes, file, indent=2)
        print(f"Recipes saved to {self.data_file}")
    
    def get_current_node(self) -> Dict:
        """Get the node at current path."""
        node = self.recipes
        for folder in self.current_path:
            node = node["folders"][folder]
        return node
    
    def display_current_path(self) -> None:
        """Display current directory path."""
        if not self.current_path:
            path_display = "/"
        else:
            path_display = "/" + "/".join(self.current_path)
        print(f"Current location: {path_display}")
    
    def list_content(self) -> None:
        """List all folders and recipes in current directory."""
        current = self.get_current_node()
        
        print("\nFolders:")
        if current["folders"]:
            for folder in sorted(current["folders"].keys()):
                print(f"  📁 {folder}")
        else:
            print("  (No folders)")
        
        print("\nRecipes:")
        if current["recipes"]:
            for recipe in sorted(current["recipes"].keys()):
                recipe_data = current["recipes"][recipe]
                price = self.calculate_recipe_price(recipe_data)
                price_display = f"(Est: ${price:.2f})" if price is not None else ""
                print(f"  📝 {recipe} {price_display}")
        else:
            print("  (No recipes)")
        print()
    
    def calculate_ingredient_price(self, ingredient_name: str, amount: float, unit: str) -> Optional[float]:
        """Calculate the price of a single ingredient."""
        ingredient_key = ingredient_name.lower()
        
        if ingredient_key in self.price_data:
            price_info = self.price_data[ingredient_key]
            price_per_unit = price_info.get("price", 0)
            price_unit = price_info.get("measurement", "")
            
            # Convert units if needed
            if unit != price_unit and unit and price_unit:
                try:
                    converted_amount = UnitConverter.convert(amount, unit, price_unit)
                    return converted_amount * price_per_unit
                except Exception as e:
                    print(f"Warning: Could not convert {unit} to {price_unit} for {ingredient_name}: {e}")
                    return None
            else:
                return amount * price_per_unit
        
        return None
    
    def calculate_recipe_price(self, recipe_data: Dict) -> Optional[float]:
        """Calculate the total price of a recipe based on ingredients."""
        if "ingredients" not in recipe_data or not recipe_data["ingredients"]:
            return None
        
        total_price = 0.0
        missing_prices = []
        
        for ingredient_name, ingredient_info in recipe_data["ingredients"].items():
            amount = ingredient_info.get("amount", 0)
            unit = ingredient_info.get("unit", "")
            
            ingredient_price = self.calculate_ingredient_price(ingredient_name, amount, unit)
            
            if ingredient_price is not None:
                total_price += ingredient_price
            else:
                missing_prices.append(ingredient_name)
        
        if missing_prices:
            if len(missing_prices) == len(recipe_data["ingredients"]):
                return None
        
        return total_price
    
    def enter_folder(self, folder_name: str) -> bool:
        """Enter a folder if it exists."""
        current = self.get_current_node()
        if folder_name in current["folders"]:
            self.current_path.append(folder_name)
            return True
        else:
            print(f"Folder '{folder_name}' doesn't exist!")
            return False
    
    def go_up(self) -> bool:
        """Go up one level if not at root."""
        if self.current_path:
            self.current_path.pop()
            return True
        else:
            print("Already at root directory!")
            return False
    
    def create_folder(self, folder_name: str) -> None:
        """Create new folder in current directory."""
        current = self.get_current_node()
        if folder_name in current["folders"]:
            print(f"Folder '{folder_name}' already exists!")
        else:
            current["folders"][folder_name] = {"folders": {}, "recipes": {}}
            self.save_recipes()
            print(f"Folder '{folder_name}' created!")
    
    def view_recipe(self, recipe_name: str) -> None:
        """View a recipe if it exists, showing ingredient prices."""
        current = self.get_current_node()
        if recipe_name in current["recipes"]:
            recipe = current["recipes"][recipe_name]
            print("\n" + "=" * 50)
            print(f"Recipe: {recipe_name}")
            print("=" * 50)
            
            # Calculate and display total price
            total_price = self.calculate_recipe_price(recipe)
            if total_price is not None:
                print(f"\nTotal Estimated Cost: ${total_price:.2f}")
            else:
                print("\nTotal Estimated Cost: Unknown (missing price data)")
            
            print("\nIngredients:")
            if isinstance(recipe["ingredients"], dict):
                # New format with amounts and units
                missing_prices = []
                
                for ingredient, details in recipe["ingredients"].items():
                    amount = details.get("amount", "")
                    unit = details.get("unit", "")
                    
                    # Calculate price for this ingredient
                    ingredient_price = None
                    if amount and (unit or True):  # Even if unit is empty, try to calculate
                        ingredient_price = self.calculate_ingredient_price(ingredient, amount, unit)
                    
                    # Format the display
                    if amount and unit:
                        ingredient_text = f"  • {ingredient}: {amount} {unit}"
                    elif amount:
                        ingredient_text = f"  • {ingredient}: {amount}"
                    else:
                        ingredient_text = f"  • {ingredient}"
                    
                    # Add price information
                    if ingredient_price is not None:
                        print(f"{ingredient_text} (${ingredient_price:.2f})")
                    else:
                        print(f"{ingredient_text} (price unknown)")
                        missing_prices.append(ingredient)
                
                # Notify about missing prices
                if missing_prices:
                    print(f"\nNote: Missing price data for: {', '.join(missing_prices)}")
            else:
                # Legacy format
                for ingredient in recipe["ingredients"]:
                    print(f"  • {ingredient}")
            
            print("\nInstructions:")
            instructions = recipe["instructions"]
            wrapped_instructions = textwrap.wrap(instructions, width=70)
            for line in wrapped_instructions:
                print(f"  {line}")
            
            if "notes" in recipe and recipe["notes"]:
                print("\nNotes:")
                notes = recipe["notes"]
                wrapped_notes = textwrap.wrap(notes, width=70)
                for line in wrapped_notes:
                    print(f"  {line}")
            
            print("\n" + "=" * 50 + "\n")
        else:
            print(f"Recipe '{recipe_name}' doesn't exist!")
    
    def create_recipe(self, recipe_name: str) -> None:
        """Create a new recipe with structured ingredients."""
        current = self.get_current_node()
        if recipe_name in current["recipes"]:
            print(f"Recipe '{recipe_name}' already exists! Use 'edit' command to modify it.")
            return
        
        print(f"\nCreating new recipe: {recipe_name}")
        ingredients = {}
        print("Enter ingredients (format: ingredient amount unit, empty line to finish):")
        print("Example: Shrimp 1 lb")
        
        while True:
            ingredient_line = input("> ").strip()
            if not ingredient_line:
                break
            
            # Parse the ingredient line
            parts = ingredient_line.split()
            if len(parts) < 1:
                print("Invalid format. Please enter at least the ingredient name.")
                continue
                
            if len(parts) == 1:
                # Just ingredient name
                ingredient_name = parts[0]
                ingredients[ingredient_name] = {}
            elif len(parts) >= 3:
                # Ingredient with amount and unit
                # The ingredient name might have spaces, so join everything except the last two parts
                amount_index = len(parts) - 2
                ingredient_name = " ".join(parts[:amount_index])
                try:
                    amount = float(parts[amount_index])
                    unit = parts[amount_index + 1]
                    ingredients[ingredient_name] = {"amount": amount, "unit": unit}
                except ValueError:
                    print("Invalid amount format. Using as ingredient name only.")
                    ingredient_name = ingredient_line
                    ingredients[ingredient_name] = {}
            elif len(parts) == 2:
                # Try to parse the second part as a number
                ingredient_name = parts[0]
                try:
                    amount = float(parts[1])
                    ingredients[ingredient_name] = {"amount": amount}
                except ValueError:
                    # If not a number, treat as a unit
                    ingredients[ingredient_name] = {"unit": parts[1]}
        
        print("\nEnter instructions (multi-line, type 'END' on a new line to finish):")
        instructions_lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            instructions_lines.append(line)
        instructions = " ".join(instructions_lines)
        
        print("\nEnter notes (optional, multi-line, type 'END' on a new line to finish):")
        notes_lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            notes_lines.append(line)
        notes = " ".join(notes_lines)
        
        current["recipes"][recipe_name] = {
            "ingredients": ingredients,
            "instructions": instructions,
            "notes": notes
        }
        
        self.save_recipes()
        print(f"Recipe '{recipe_name}' created successfully!")
        
        # Calculate and show price
        price = self.calculate_recipe_price(current["recipes"][recipe_name])
        if price is not None:
            print(f"Estimated cost: ${price:.2f}")
        else:
            print("Could not calculate price due to missing ingredient price data.")
    
    def edit_recipe(self, recipe_name: str) -> None:
        """Edit an existing recipe."""
        current = self.get_current_node()
        if recipe_name not in current["recipes"]:
            print(f"Recipe '{recipe_name}' doesn't exist!")
            return
        
        recipe = current["recipes"][recipe_name]
        print(f"\nEditing recipe: {recipe_name}")
        
        # Display current ingredients
        print("\nCurrent ingredients:")
        if isinstance(recipe["ingredients"], dict):
            # New format
            for i, (ingredient, details) in enumerate(recipe["ingredients"].items(), 1):
                amount = details.get("amount", "")
                unit = details.get("unit", "")
                
                # Calculate price for this ingredient
                ingredient_price = None
                if amount and (unit or True):  # Even if unit is empty, try to calculate
                    ingredient_price = self.calculate_ingredient_price(ingredient, amount, unit)
                
                # Format display
                if amount and unit:
                    ingredient_text = f"  {i}. {ingredient}: {amount} {unit}"
                elif amount:
                    ingredient_text = f"  {i}. {ingredient}: {amount}"
                elif unit:
                    ingredient_text = f"  {i}. {ingredient}: {unit}"
                else:
                    ingredient_text = f"  {i}. {ingredient}"
                
                # Add price
                if ingredient_price is not None:
                    print(f"{ingredient_text} (${ingredient_price:.2f})")
                else:
                    print(f"{ingredient_text} (price unknown)")
        else:
            # Legacy format
            for i, ingredient in enumerate(recipe["ingredients"], 1):
                print(f"  {i}. {ingredient}")
        
        choice = input("\nEdit ingredients? (y/n): ").lower()
        if choice == 'y':
            ingredients = {}
            print("Enter ingredients (format: ingredient amount unit, empty line to finish):")
            print("Example: Shrimp 1 lb")
            
            while True:
                ingredient_line = input("> ").strip()
                if not ingredient_line:
                    break
                
                # Parse the ingredient line
                parts = ingredient_line.split()
                if len(parts) < 1:
                    print("Invalid format. Please enter at least the ingredient name.")
                    continue
                    
                if len(parts) == 1:
                    # Just ingredient name
                    ingredient_name = parts[0]
                    ingredients[ingredient_name] = {}
                elif len(parts) >= 3:
                    # Ingredient with amount and unit
                    # The ingredient name might have spaces, so join everything except the last two parts
                    amount_index = len(parts) - 2
                    ingredient_name = " ".join(parts[:amount_index])
                    try:
                        amount = float(parts[amount_index])
                        unit = parts[amount_index + 1]
                        ingredients[ingredient_name] = {"amount": amount, "unit": unit}
                    except ValueError:
                        print("Invalid amount format. Using as ingredient name only.")
                        ingredient_name = ingredient_line
                        ingredients[ingredient_name] = {}
                elif len(parts) == 2:
                    # Try to parse the second part as a number
                    ingredient_name = parts[0]
                    try:
                        amount = float(parts[1])
                        ingredients[ingredient_name] = {"amount": amount}
                    except ValueError:
                        # If not a number, treat as a unit
                        ingredients[ingredient_name] = {"unit": parts[1]}
            
            recipe["ingredients"] = ingredients
        
        print("\nCurrent instructions:")
        wrapped_instructions = textwrap.wrap(recipe["instructions"], width=70)
        for line in wrapped_instructions:
            print(f"  {line}")
        
        choice = input("\nEdit instructions? (y/n): ").lower()
        if choice == 'y':
            print("Enter instructions (multi-line, type 'END' on a new line to finish):")
            instructions_lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                instructions_lines.append(line)
            recipe["instructions"] = " ".join(instructions_lines)
        
        print("\nCurrent notes:")
        if "notes" in recipe and recipe["notes"]:
            wrapped_notes = textwrap.wrap(recipe["notes"], width=70)
            for line in wrapped_notes:
                print(f"  {line}")
        else:
            print("  (No notes)")
        
        choice = input("\nEdit notes? (y/n): ").lower()
        if choice == 'y':
            print("Enter notes (multi-line, type 'END' on a new line to finish):")
            notes_lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                notes_lines.append(line)
            recipe["notes"] = " ".join(notes_lines)
        
        self.save_recipes()
        print(f"Recipe '{recipe_name}' updated successfully!")
        
        # Calculate and show updated price
        price = self.calculate_recipe_price(recipe)
        if price is not None:
            print(f"Updated estimated cost: ${price:.2f}")
    
    def add_ingredient_price(self, ingredient_name: str, price: float, measurement: str) -> None:
        """Add or update an ingredient price in the price database."""
        self.price_data[ingredient_name.lower()] = {
            "price": price,
            "measurement": measurement
        }
        self.save_price_data()
        print(f"Price data for '{ingredient_name}' added/updated.")
    
    def delete_recipe(self, recipe_name: str) -> None:
        """Delete a recipe if it exists."""
        current = self.get_current_node()
        if recipe_name in current["recipes"]:
            confirm = input(f"Are you sure you want to delete '{recipe_name}'? (y/n): ").lower()
            if confirm == 'y':
                del current["recipes"][recipe_name]
                self.save_recipes()
                print(f"Recipe '{recipe_name}' deleted!")
            else:
                print("Deletion cancelled.")
        else:
            print(f"Recipe '{recipe_name}' doesn't exist!")
    
    def delete_folder(self, folder_name: str) -> None:
        """Delete a folder if it exists and is empty."""
        current = self.get_current_node()
        if folder_name in current["folders"]:
            folder = current["folders"][folder_name]
            if folder["folders"] or folder["recipes"]:
                print(f"Folder '{folder_name}' is not empty! Delete contents first.")
            else:
                confirm = input(f"Are you sure you want to delete folder '{folder_name}'? (y/n): ").lower()
                if confirm == 'y':
                    del current["folders"][folder_name]
                    self.save_recipes()
                    print(f"Folder '{folder_name}' deleted!")
                else:
                    print("Deletion cancelled.")
        else:
            print(f"Folder '{folder_name}' doesn't exist!")
    
    def move_recipe(self, recipe_name: str, destination_path: str) -> None:
        """Move a recipe to a different folder."""
        current = self.get_current_node()
        if recipe_name not in current["recipes"]:
            print(f"Recipe '{recipe_name}' doesn't exist!")
            return
        
        # Parse destination path
        path_parts = [p for p in destination_path.split("/") if p]
        
        # Navigate to destination
        if destination_path.startswith("/"):
            # Absolute path
            dest_node = self.recipes
            full_path = []
        else:
            # Relative path
            dest_node = self.get_current_node()
            full_path = self.current_path.copy()
        
        for part in path_parts:
            if part == "..":
                if full_path:
                    full_path.pop()
                    # Recalculate dest_node based on new full_path
                    dest_node = self.recipes
                    for folder in full_path:
                        dest_node = dest_node["folders"][folder]
            elif part in dest_node["folders"]:
                full_path.append(part)
                dest_node = dest_node["folders"][part]
            else:
                print(f"Destination folder '{part}' doesn't exist!")
                return
        
        # Perform the move
        recipe_data = current["recipes"][recipe_name]
        dest_node["recipes"][recipe_name] = recipe_data
        del current["recipes"][recipe_name]
        self.save_recipes()
        
        # Display the path where recipe was moved
        dest_path_str = "/" + "/".join(full_path) if full_path else "/"
        print(f"Recipe '{recipe_name}' moved to {dest_path_str}")
    
    def search_recipes(self, query: str) -> None:
        """Search for recipes containing the query in name or ingredients."""
        results = []
        
        def search_node(node, path):
            for recipe_name, recipe_data in node["recipes"].items():
                # Search in name
                if query.lower() in recipe_name.lower():
                    results.append((path, recipe_name, "name"))
                    continue
                
                # Search in ingredients
                if isinstance(recipe_data["ingredients"], dict):
                    # New format
                    for ingredient in recipe_data["ingredients"].keys():
                        if query.lower() in ingredient.lower():
                            results.append((path, recipe_name, "ingredient"))
                            break
                else:
                    # Legacy format
                    for ingredient in recipe_data["ingredients"]:
                        if query.lower() in ingredient.lower():
                            results.append((path, recipe_name, "ingredient"))
                            break
            
            for folder_name, folder_data in node["folders"].items():
                new_path = path + [folder_name]
                search_node(folder_data, new_path)
        
        search_node(self.recipes, [])
        
        if results:
            print(f"\nFound {len(results)} results for '{query}':")
            for path, recipe_name, match_type in results:
                path_str = "/" + "/".join(path) if path else "/"
                price = None
                
                # Get the recipe to calculate price
                node = self.recipes
                for folder in path:
                    node = node["folders"][folder]
                
                if recipe_name in node["recipes"]:
                    price = self.calculate_recipe_price(node["recipes"][recipe_name])
                
                price_display = f" (Est: ${price:.2f})" if price is not None else ""
                match_info = f"matched in {match_type}"
                print(f"  {recipe_name}{price_display} (in {path_str}) - {match_info}")
        else:
            print(f"No recipes found containing '{query}'")
    
    def print_help(self) -> None:
        """Print available commands."""
        print("\nAvailable commands:")
        print("  ls                      List contents of current directory")
        print("  cd <folder>             Enter a folder")
        print("  cd ..                   Go up one level")
        print("  mkdir <folder>          Create a new folder")
        print("  rmdir <folder>          Remove an empty folder")
        print("  view <recipe>           View a recipe")
        print("  create <recipe>         Create a new recipe")
        print("  edit <recipe>           Edit an existing recipe")
        print("  delete <recipe>         Delete a recipe")
        print("  move <recipe> <path>    Move a recipe to another folder")
        print("  search <query>          Search for recipes")
        print("  price <ingredient> <price> <unit>  Add/update ingredient price")
        print("  help                    Display this help message")
        print("  exit                    Exit the application")
    
    def run(self) -> None:
        """Run the recipe manager CLI."""
        print("\n" + "=" * 50)
        print("Welcome to Recipe Manager!")
        print("=" * 50)
        print("Type 'help' for available commands.")
        
        while True:
            self.display_current_path()
            command = input("> ").strip()
            
            if not command:
                continue
            
            parts = command.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            
            if cmd == "exit":
                print("Goodbye!")
                break
            elif cmd == "help":
                self.print_help()
            elif cmd == "ls":
                self.list_content()
            elif cmd == "cd":
                if arg == "..":
                    self.go_up()
                elif arg:
                    self.enter_folder(arg)
                else:
                    print("Usage: cd <folder> or cd ..")
            elif cmd == "mkdir":
                if arg:
                    self.create_folder(arg)
                else:
                    print("Usage: mkdir <folder>")
            elif cmd == "rmdir":
                if arg:
                    self.delete_folder(arg)
                else:
                    print("Usage: rmdir <folder>")
            elif cmd == "view":
                if arg:
                    self.view_recipe(arg)
                else:
                    print("Usage: view <recipe>")
            elif cmd == "create":
                if arg:
                    self.create_recipe(arg)
                else:
                    print("Usage: create <recipe>")
            elif cmd == "edit":
                if arg:
                    self.edit_recipe(arg)
                else:
                    print("Usage: edit <recipe>")
            elif cmd == "delete":
                if arg:
                    self.delete_recipe(arg)
                else:
                    print("Usage: delete <recipe>")
            elif cmd == "move":
                parts = arg.split(maxsplit=1)
                if len(parts) == 2:
                    recipe_name, dest_path = parts
                    self.move_recipe(recipe_name, dest_path)
                else:
                    print("Usage: move <recipe> <destination_path>")
            elif cmd == "search":
                if arg:
                    self.search_recipes(arg)
                else:
                    print("Usage: search <query>")
            elif cmd == "price":
                parts = arg.split()
                if len(parts) >= 3:
                    ingredient_name = " ".join(parts[:-2])
                    try:
                        price = float(parts[-2])
                        unit = parts[-1]
                        self.add_ingredient_price(ingredient_name, price, unit)
                    except ValueError:
                        print("Invalid price format. Usage: price <ingredient> <price> <unit>")
                else:
                    print("Usage: price <ingredient> <price> <unit>")
                    print("Example: price Onion 1 oz")
            else:
                print(f"Unknown command: {cmd}. Type 'help' for available commands.")

if __name__ == "__main__":
    manager = RecipeManager()
    manager.run()