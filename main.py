import os
from RefEmployees import (
    SalariedEmployee, HourlyEmployee, Freelancer, Intern,
    ManagerVacationPolicy, VPVacationPolicy, DefaultVacationPolicy, InternVacationPolicy, FreelancerVacationPolicy,
    load_payment_policies_from_json
)

class EmployeeFactory:
    def __init__(self, policies):
        self.policies = policies

    def create_employee(self, name, role, emp_type):
        if emp_type == "salaried":
            salary = float(input("Salario mensual: "))
            vac_policy = self._get_vacation_policy(role)
            return SalariedEmployee(name, role, salary, vac_policy, self.policies["salaried"])

        elif emp_type == "hourly":
            rate = float(input("Tarifa por hora: "))
            hours = int(input("Horas trabajadas: "))
            vac_policy = self._get_vacation_policy(role)
            return HourlyEmployee(name, role, rate, hours, vac_policy, self.policies["hourly"])

        elif emp_type == "freelancer":
            projects = []
            while True:
                pname = input("Nombre del proyecto (o 'fin' para terminar): ") #ROMPER FLUJO B Y LLEVARLO AL FLUJO INICIAL AL CREAR ROL
                if pname.lower() == "fin":
                    break
                amount = float(input("Monto del proyecto: "))
                projects.append({"name": pname, "amount": amount})
            return Freelancer(name, projects, DefaultVacationPolicy(), self.policies["freelancer"])

        elif emp_type == "intern":
            return Intern(name, InternVacationPolicy(), self.policies["intern"])

        else:
            raise ValueError("Tipo de empleado no válido.")

    def _get_vacation_policy(self, role):
        policies = {
            "manager": ManagerVacationPolicy(),
            "vice_president": VPVacationPolicy(),
            "intern": InternVacationPolicy(),
            "freelancer": FreelancerVacationPolicy()
        }
        return policies.get(role, DefaultVacationPolicy())


class EmployeeManager:
    def __init__(self):
        self.employees = []
        self.policies = load_payment_policies_from_json()
        self.factory = EmployeeFactory(self.policies)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def run(self):
        while True:
            self.clear_screen()
            print("--- Menú de Gestión de Empleados ---")
            print("1. Crear empleado")
            print("2. Ver empleados por rol")
            print("3. Solicitar vacaciones")
            print("4. Pagar empleados")
            print("5. Ver historial de transacciones")
            print("0. Salir")

            choice = input("Seleccione una opción: ")

            if choice == "1":
                self.create_employee()
            elif choice == "2":
                self.view_by_role()
            elif choice == "3":
                self.request_vacation()
            elif choice == "4":
                self.pay_employees()
            elif choice == "5":
                self.view_transactions()
            elif choice == "0":
                print("¡Hasta luego!")
                break
            else:
                print("Opción no válida.")
                input("Presione Enter para continuar...")

    def create_employee(self):
        name = input("Nombre del empleado: ")
        role = input("Rol (intern, manager, vice_president, freelancer): ").lower()

        if role == "freelancer":
            emp_type = "freelancer"  # Se agrega el nuevo flujo para freelancer
        else:
            emp_type = input("Tipo de pago para el empleado (salaried/hourly): ").lower()

        try:
            employee = self.factory.create_employee(name, role, emp_type)
            self.employees.append(employee)
            print("Empleado creado exitosamente.")
        except Exception as e:
            print(f"Error: {e}")
        input("Presione Enter para continuar...")


    def view_by_role(self):
        while True:
            self.clear_screen()
            print("--- Submenú de Visualización de Empleados ---")
            print("1. Ver managers")
            print("2. Ver interns")
            print("3. Ver vice presidents")
            print("4. Ver freelancers")
            print("5. Ver todos los empleados")
            print("0. Volver al menú principal")

            sub_choice = input("Seleccione una opción: ")

            if sub_choice == "1":
                self._print_employees_by_role("manager")
            elif sub_choice == "2":
                self._print_employees_by_role("intern") 
            elif sub_choice == "3":
                self._print_employees_by_role("vice_president")
            elif sub_choice == "4":
                self._print_employees_by_role("freelancer")
            elif sub_choice == "5":
                for emp in self.employees:
                    print(f"{emp.name} ({emp.role}) - {emp.vacation_days} vacation days")   
            elif sub_choice == "0":
                break
            else:
                print("Opción inválida.")
            input("Presione Enter para continuar...")

    def _print_employees_by_role(self, role):
        for emp in self.employees:
            if emp.role == role:
                print(f"{emp.name} ({emp.role}) - {emp.vacation_days} días de vacaciones")

    def request_vacation(self):
        self.clear_screen()
        valid_employees = [emp for emp in self.employees if emp.can_request_vacation()]

        if not valid_employees:
            print("No hay empleados elegibles para vacaciones.")
            input("Presione Enter para continuar...")
            return

        for idx, emp in enumerate(valid_employees):
            print(f"{idx}. {emp.name} ({emp.role}) - {emp.vacation_days} días de vacaciones")

        try:
            idx = int(input("Seleccione el índice del empleado: "))
            days = int(input("Días de vacaciones: "))
            payout = input("¿Payout en lugar de tiempo libre? (s/n): ").lower() == "s"
            valid_employees[idx].request_vacation(days, payout)
            print("Vacaciones registradas.")
        except Exception as e:
            print(f"Error: {e}")
            input("Presione Enter para continuar...")


    def pay_employees(self):
        self.clear_screen()
        for emp in self.employees:
            try:
                total = emp.calculate_payment()
                print(f"{emp.name} recibió ${total}")
            except Exception as e:
                print(f"Error al pagar a {emp.name}: {e}")
        input("Presione Enter para continuar...")

    def view_transactions(self):
        self.clear_screen()
        for idx, emp in enumerate(self.employees):
            print(f"{idx}. {emp.name} ({emp.role})")
        try:
            idx = int(input("Seleccione el índice del empleado: "))
            self.employees[idx].show_transactions() 
        except Exception as e:
            print(f"Error: {e}")
        input("Presione Enter para continuar...")

if __name__ == "__main__":
    manager = EmployeeManager()
    manager.run()
