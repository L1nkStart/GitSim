"""
Main entry point for the Git simulation system.
"""
from git_sim.cli import GitSimCLI

def main():
    cli = GitSimCLI()
    print("Git Simulation System")
    print("Type 'help' for command list")
    print("Type 'exit' to quit")
    
    while True:
        try:
            command = input("git-sim> ").strip()
            if command.lower() == "exit":
                break
            
            if command.lower() == "help":
                print(cli.get_help())
                continue
            
            if command.startswith("git"):
                print("No incluir la palabra 'git' en los comandos")
                continue
            
            parts = command.split()
            if not parts:
                continue
            
            result = cli.execute(parts[0], *parts[1:])
            print(result)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()