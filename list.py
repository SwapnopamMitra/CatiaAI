import os

def list_directory_structure(root_dir, indent=""):
    """Recursively lists all files and subdirectories in a formatted tree view."""
    items = sorted(os.listdir(root_dir))
    
    for index, item in enumerate(items):
        path = os.path.join(root_dir, item)
        is_last = (index == len(items) - 1)
        prefix = "└── " if is_last else "│── "

        if os.path.isdir(path):
            print(f"{indent}{prefix}{item}/")
            new_indent = indent + ("    " if is_last else "│   ")
            list_directory_structure(path, new_indent)
        else:
            print(f"{indent}{prefix}{item}")

if __name__ == "__main__":
    project_dir = os.getcwd()  # Get current directory
    print(f"/{os.path.basename(project_dir)}/")
    list_directory_structure(project_dir)
