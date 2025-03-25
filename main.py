"""
Punto de entrada principal para el sistema de la simulacion de git
"""
from git_sim.cli import GitSimCLI

def main():
    cli = GitSimCLI()
    print("Sistema Simulado de Git")
    print("Escribe 'help' para obtener la lista de comandos")
    print("Escribe 'exit' para salir")
    
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
            print("\nSaliendo...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
