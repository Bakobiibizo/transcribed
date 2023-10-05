
def set_file_permissions_recursively(file_path):
    for item in file_path.iterdir():
        if item.is_file() or item.is_dir():
            item.chmod(0o777)
        if item.is_dir():
            set_file_permissions_recursively(item)

                
def main():
    # Set bash_install.sh paths
    bash_path = path.cwd() / 
    
    # Create bash_install.sh
    bash_path.write_text(install_sh)

    # Set permissions
    set_file_permissions_recursively(path.cwd())
    
    subprocess.run(["sudo", "bash", "bash_install.sh"])
    
    
    print("Instillation complete. Restart your terminal and then run run.sh to start the server.")
    
if __name__ == "__main__":
    main()