import os
import json
import textwrap
from typing import Dict, List, Any, Optional

class RecipeManager:
    def __init__(self, data_file: str = "recipes.json"):
        self.data_file = data_file
        self.recipes = self.load_recipes()
        self.current_path = []
        
    """Load recipes from JSON file or create a new structure."""
    def load_recipes(self) -> Dict:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print(f"Error reading {self.data_file}, creating new recipe database.")
                return {"folders": {}, "recipes": {}}
        else:
            return {"folders": {}, "recipes": {}}
    
    """Save recipes to JSON file."""
    def save_recipes(self) -> None:
        with open(self.data_file, 'w') as file:
            json.dump(self.recipes, file, indent=2)
        print(f"Recipes saved to {self.data_file}")
    
    """Get the node at current path."""
    def get_current_node(self) -> Dict:
        node = self.recipes
        for folder in self.current_path:
            node = node["folders"][folder]
        return node
    
    """Display current directory path."""
    def display_current_path(self) -> None:
        if not self.current_path:
            path_display = "/"
        else:
            path_display = "/" + "/".join(self.current_path)
        print(f"Current location: {path_display}")
    
    """List all folders and recipes in current directory."""
    def list_content(self) -> None:
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
                print(f"  📝 {recipe}")
        else:
            print("  (No recipes)")
        print()
    
    """Enter a folder if it exists."""
    def enter_folder(self, folder_name: str) -> bool:
        current = self.get_current_node()
        if folder_name in current["folders"]:
            self.current_path.append(folder_name)
            return True
        else:
            print(f"Folder '{folder_name}' doesn't exist!")
            return False
    
    """Go up one level if not at root."""
    def go_up(self) -> bool:
        if self.current_path:
            self.current_path.pop()
            return True
        else:
            print("Already at root directory!")
            return False
    
    """Create new folder in current directory."""
    def create_folder(self, folder_name: str) -> None:
        current = self.get_current_node()
        if folder_name in current["folders"]:
            print(f"Folder '{folder_name}' already exists!")
        else:
            current["folders"][folder_name] = {"folders": {}, "recipes": {}}
            self.save_recipes()
            print(f"Folder '{folder_name}' created!")
    
    """View a recipe if it exists."""
    def view_recipe(self, recipe_name: str) -> None:
        current = self.get_current_node()
        if recipe_name in current["recipes"]:
            recipe = current["recipes"][recipe_name]
            print("\n" + "=" * 50)
            print(f"Recipe: {recipe_name}")
            print("=" * 50)
            
            print("\nIngredients:")
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
    
    """Create a new recipe."""
    def create_recipe(self, recipe_name: str) -> None:
        current = self.get_current_node()
        if recipe_name in current["recipes"]:
            print(f"Recipe '{recipe_name}' already exists! Use 'edit' command to modify it.")
            return
        
        print(f"\nCreating new recipe: {recipe_name}")
        ingredients = []
        print("Enter ingredients (one per line, empty line to finish):")
        while True:
            ingredient = input("> ").strip()
            if not ingredient:
                break
            ingredients.append(ingredient)
        
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
    
    """Edit an existing recipe."""
    def edit_recipe(self, recipe_name: str) -> None:
        current = self.get_current_node()
        if recipe_name not in current["recipes"]:
            print(f"Recipe '{recipe_name}' doesn't exist!")
            return
        
        recipe = current["recipes"][recipe_name]
        print(f"\nEditing recipe: {recipe_name}")
        
        print("\nCurrent ingredients:")
        for i, ingredient in enumerate(recipe["ingredients"], 1):
            print(f"  {i}. {ingredient}")
        
        choice = input("\nEdit ingredients? (y/n): ").lower()
        if choice == 'y':
            ingredients = []
            print("Enter ingredients (one per line, empty line to finish):")
            while True:
                ingredient = input("> ").strip()
                if not ingredient:
                    break
                ingredients.append(ingredient)
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
    
    """Delete a recipe if it exists."""
    def delete_recipe(self, recipe_name: str) -> None:
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
    
    """Delete a folder if it exists and is empty."""
    def delete_folder(self, folder_name: str) -> None:
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
    
    """Move a recipe to a different folder."""
    def move_recipe(self, recipe_name: str, destination_path: str) -> None:
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
    
    """Search for recipes containing the query in name or ingredients."""
    def search_recipes(self, query: str) -> None:
        results = []
        
        def search_node(node, path):
            for recipe_name, recipe_data in node["recipes"].items():
                if (query.lower() in recipe_name.lower() or 
                    any(query.lower() in ingredient.lower() for ingredient in recipe_data["ingredients"])):
                    results.append((path, recipe_name))
            
            for folder_name, folder_data in node["folders"].items():
                new_path = path + [folder_name]
                search_node(folder_data, new_path)
        
        search_node(self.recipes, [])
        
        if results:
            print(f"\nFound {len(results)} results for '{query}':")
            for path, recipe_name in results:
                path_str = "/" + "/".join(path) if path else "/"
                print(f"  {recipe_name} (in {path_str})")
        else:
            print(f"No recipes found containing '{query}'")
    
    """Print available commands."""
    def print_help(self) -> None:
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
        print("  help                    Display this help message")
        print("  exit                    Exit the application")
    
    """Run the recipe manager CLI."""
    def run(self) -> None:
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
            else:
                print(f"Unknown command: {cmd}. Type 'help' for available commands.")

if __name__ == "__main__":
    manager = RecipeManager()
    manager.run()
