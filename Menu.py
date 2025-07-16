import os
from RefEmployees import (
    SalariedEmployee, HourlyEmployee, Freelancer, Intern,
    ManagerVacationPolicy, VPVacationPolicy, DefaultVacationPolicy, InternVacationPolicy,
    load_payment_policies_from_json
)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    employees = []
    policies = load_payment_policies_from_json()

    while True:
        clear_screen()
        print("--- Menú de Gestión de Empleados ---")
        print("1. Crear empleado")
        print("2. Ver empleados por rol")
        print("3. Solicitar vacaciones")
        print("4. Pagar empleados")
        print("5. Ver historial de transacciones")
        print("0. Salir")

        choice = input("Seleccione una opción: ")

        if choice == "1":
            name = input("Nombre del empleado: ")
            role = input("Rol (intern, manager, vice_president, otro): ").lower()
            emp_type = input("Tipo de empleado (salaried/hourly/freelancer/intern): ").lower()

            if emp_type == "salaried":
                salary = float(input("Salario mensual: "))
                vac_policy = ManagerVacationPolicy() if role == "manager" else VPVacationPolicy() if role == "vice_president" else DefaultVacationPolicy()
                employee = SalariedEmployee(name, role, salary, vac_policy, policies["salaried"])

            elif emp_type == "hourly":
                rate = float(input("Tarifa por hora: "))
                hours = int(input("Horas trabajadas: "))
                vac_policy = ManagerVacationPolicy() if role == "manager" else VPVacationPolicy() if role == "vice_president" else DefaultVacationPolicy()
                employee = HourlyEmployee(name, role, rate, hours, vac_policy, policies["hourly"])

            elif emp_type == "freelancer":
                projects = []
                while True:
                    pname = input("Nombre del proyecto (o 'fin' para terminar): ")
                    if pname.lower() == "fin":
                        break
                    amount = float(input("Monto del proyecto: "))
                    projects.append({"name": pname, "amount": amount})
                employee = Freelancer(name, projects, DefaultVacationPolicy(), policies["freelancer"])

            elif emp_type == "intern":
                employee = Intern(name, InternVacationPolicy(), policies["intern"])

            else:
                print("Tipo de empleado no válido.")
                input("Presione Enter para continuar...")
                continue

            employees.append(employee)
            print("Empleado creado exitosamente.")
            input("Presione Enter para continuar...")

        elif choice == "2":
            while True:
                clear_screen()
                print("--- Submenú de Visualización de Empleados ---")
                print("1. Ver managers")
                print("2. Ver interns")
                print("3. Ver vice presidents")
                print("0. Volver al menú principal")

                sub_choice = input("Seleccione una opción: ")

                if sub_choice == "1":
                    for emp in employees:
                        if emp.role == "manager":
                            print(f"{emp.name} ({emp.role}) - {emp.vacation_days} días de vacaciones")
                elif sub_choice == "2":
                    for emp in employees:
                        if emp.role == "intern":
                            print(f"{emp.name} ({emp.role}) - {emp.vacation_days} días de vacaciones")
                elif sub_choice == "3":
                    for emp in employees:
                        if emp.role == "vice_president":
                            print(f"{emp.name} ({emp.role}) - {emp.vacation_days} días de vacaciones")
                elif sub_choice == "0":
                    break
                else:
                    print("Opción inválida.")
                input("Presione Enter para continuar...")

        elif choice == "3":
            clear_screen()
            if not employees:
                print("No hay empleados disponibles.")
                input("Presione Enter para continuar...")
                continue

            for idx, emp in enumerate(employees):
                print(f"{idx}. {emp.name} ({emp.role}) - {emp.vacation_days} días de vacaciones")
            try:
                idx = int(input("Seleccione el índice del empleado: "))
                days = int(input("Días de vacaciones: "))
                payout = input("¿Payout en lugar de tiempo libre? (s/n): ").lower() == "s"
                employees[idx].request_vacation(days, payout)
                print("Vacaciones registradas.")
            except Exception as e:
                print(f"Error: {e}")
            input("Presione Enter para continuar...")

        elif choice == "4":
            clear_screen()
            for emp in employees:
                try:
                    total = emp.calculate_payment()
                    print(f"{emp.name} recibió ${total}")
                except Exception as e:
                    print(f"Error al pagar a {emp.name}: {e}")
            input("Presione Enter para continuar...")

        elif choice == "5":
            clear_screen()
            for idx, emp in enumerate(employees):
                print(f"{idx}. {emp.name} ({emp.role})")
            try:
                idx = int(input("Seleccione el índice del empleado: "))
                employees[idx].show_transactions()
            except Exception as e:
                print(f"Error: {e}")
            input("Presione Enter para continuar...")

        elif choice == "0":
            print("¡Hasta luego!")
            break

        else:
            print("Opción no válida.")
            input("Presione Enter para continuar...")

if __name__ == "__main__":
    main()
