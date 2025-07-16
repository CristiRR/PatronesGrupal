from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
import json

# Interfaces de políticas (Bridge)
class VacationPolicy(ABC):
    @abstractmethod
    def request_vacation(self, employee, days: int, payout: bool): pass

class PaymentPolicy(ABC):
    @abstractmethod
    def calculate_payment(self, employee): pass

# Visitor para operaciones por tipo
class EmployeeVisitor(ABC):
    @abstractmethod
    def visit_salaried(self, employee): pass

    @abstractmethod
    def visit_hourly(self, employee): pass

    @abstractmethod
    def visit_freelancer(self, employee): pass

    @abstractmethod
    def visit_intern(self, employee): pass



class Employee(ABC):
    def __init__(self, name, role, vacation_policy, payment_policy):
        self.name = name
        self.role = role
        self.vacation_days = 25
        self.vacation_policy = vacation_policy
        self.payment_policy = payment_policy
        self.transactions: List[dict] = []

    def request_vacation(self, days: int, payout: bool):
        self.vacation_policy.request_vacation(self, days, payout)

    def calculate_payment(self):
        return self.payment_policy.calculate_payment(self)

    @abstractmethod
    def accept(self, visitor: EmployeeVisitor): pass

    def log_transaction(self, type_op, amount, description):
        self.transactions.append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": type_op,
            "amount": amount,
            "description": description
        })

    def show_transactions(self):
        print(f"--- Historial de transacciones de {self.name} ---")
        for t in sorted(self.transactions, key=lambda x: x["date"], reverse=True):
            print(f"{t['date']} | {t['type']} | ${t['amount']} | {t['description']}")



class SalariedPaymentPolicy(PaymentPolicy):
    def __init__(self, bonus_percent=0.10):
        self.bonus_percent = bonus_percent

    def calculate_payment(self, employee):
        bonus = employee.salary * self.bonus_percent
        total = employee.salary + bonus
        employee.log_transaction("payment", total, f"Salaried + {self.bonus_percent*100:.0f}% bonus")
        return total

class HourlyPaymentPolicy(PaymentPolicy):
    def __init__(self, bonus_threshold=160, bonus_amount=100):
        self.bonus_threshold = bonus_threshold
        self.bonus_amount = bonus_amount

    def calculate_payment(self, employee):
        base = employee.rate * employee.hours
        bonus = self.bonus_amount if employee.hours > self.bonus_threshold else 0
        total = base + bonus
        employee.log_transaction("payment", total, "Hourly + bonus if > threshold")
        return total

class FreelancerPaymentPolicy(PaymentPolicy):
    def calculate_payment(self, employee):
        total = sum(p["amount"] for p in employee.projects)
        employee.log_transaction("payment", total, "Freelancer project payout")
        return total

class InternPaymentPolicy(PaymentPolicy):
    def calculate_payment(self, employee):
        employee.log_transaction("payment", 0, "Interns not paid")
        return 0



class InternVacationPolicy(VacationPolicy):
    def request_vacation(self, employee, days, payout):
        raise Exception("Interns cannot take vacations or payouts.")

class ManagerVacationPolicy(VacationPolicy):
    def request_vacation(self, employee, days, payout):
        if payout and days > 10:
            raise Exception("Managers can only request up to 10 days payout.")
        if employee.vacation_days < days:
            raise Exception("Not enough vacation days.")
        employee.vacation_days -= days
        employee.log_transaction("vacation", days, "Manager vacation/payout")

class VPVacationPolicy(VacationPolicy):
    def request_vacation(self, employee, days, payout):
        if days > 5:
            raise Exception("VPs can only request 5 days per request.")
        employee.log_transaction("vacation", days, "VP vacation/payout")

class DefaultVacationPolicy(VacationPolicy):
    def request_vacation(self, employee, days, payout):
        if employee.vacation_days < days:
            raise Exception("Not enough vacation days.")
        employee.vacation_days -= days
        employee.log_transaction("vacation", days, "Standard vacation/payout")




def load_payment_policies_from_json(path="pago.json"):
    with open(path, "r") as f:
        config = json.load(f)
    return {
        "salaried": SalariedPaymentPolicy(config["salaried"]["bonus_percent"]),
        "hourly": HourlyPaymentPolicy(config["hourly"]["bonus_threshold"], config["hourly"]["bonus_amount"]),
        "freelancer": FreelancerPaymentPolicy(),
        "intern": InternPaymentPolicy()
    }



if __name__ == "__main__":
    policies = load_payment_policies_from_json()

    emp1 = SalariedEmployee("Alice", "manager", 5000, ManagerVacationPolicy(), policies["salaried"])
    emp2 = HourlyEmployee("Bob", "developer", 30, 170, DefaultVacationPolicy(), policies["hourly"])
    emp3 = Intern("Charlie", InternVacationPolicy(), policies["intern"])
    emp4 = Freelancer("Diana", [{"name": "Website", "amount": 1200}, {"name": "App", "amount": 1800}], DefaultVacationPolicy(), policies["freelancer"])

    for emp in [emp1, emp2, emp3, emp4]:
        try:
            print(f"{emp.name} will be paid: ${emp.calculate_payment()}")
        except Exception as e:
            print(f"Error paying {emp.name}: {e}")

    try:
        emp1.request_vacation(5, payout=True)
        emp2.request_vacation(2, payout=False)
        emp3.request_vacation(1, payout=False)
    except Exception as e:
        print(f"Vacation error: {e}")

    for emp in [emp1, emp2, emp3, emp4]:
        emp.show_transactions()
        print()



#Menu 
def main():
    employees = []
    policies = load_payment_policies_from_json()

    while True:
        print("\n--- Menú de Gestión de Empleados ---")
        print("1. Crear empleado")
        print("2. Ver empleados")
        print("3. Pagar empleados")
        print("4. Solicitar vacaciones")
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
                continue

            employees.append(employee)
            print("Empleado creado exitosamente.")

        elif choice == "2":
            print("\n--- Lista de Empleados ---")
            for idx, emp in enumerate(employees):
                print(f"{idx}. {emp.name} ({emp.role})")

        elif choice == "3":
            print("\n--- Pagando empleados ---")
            for emp in employees:
                try:
                    total = emp.calculate_payment()
                    print(f"{emp.name} recibió ${total}")
                except Exception as e:
                    print(f"Error al pagar a {emp.name}: {e}")

        elif choice == "4":
            print("\n--- Solicitud de vacaciones ---")
            for idx, emp in enumerate(employees):
                print(f"{idx}. {emp.name} ({emp.role})")
            try:
                idx = int(input("Seleccione el índice del empleado: "))
                days = int(input("Días de vacaciones: "))
                payout = input("¿Payout en lugar de tiempo libre? (s/n): ").lower() == "s"
                employees[idx].request_vacation(days, payout)
                print("Vacaciones registradas.")
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "5":
            print("\n--- Historial de transacciones ---")
            for idx, emp in enumerate(employees):
                print(f"{idx}. {emp.name} ({emp.role})")
            try:
                idx = int(input("Seleccione el índice del empleado: "))
                employees[idx].show_transactions()
            except Exception as e:
                print(f"Error: {e}")

        elif choice == "0":
            print("¡Hasta luego!")
            break

        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()
