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

# Clase base de Empleado

class Employee(ABC):
    def __init__(self, name, role, vacation_policy, payment_policy):
        self.name = name
        self.role = role
        self.vacation_days = 10
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

    def can_request_vacation(self) -> bool:
        return True

class SalariedEmployee(Employee):
    def __init__(self, name, role, salary, vacation_policy, payment_policy):
        super().__init__(name, role, vacation_policy, payment_policy)
        self.salary = salary

    def accept(self, visitor: EmployeeVisitor):
        return visitor.visit_salaried(self)

class HourlyEmployee(Employee):
    def __init__(self, name, role, rate, hours, vacation_policy, payment_policy):
        super().__init__(name, role, vacation_policy, payment_policy)
        self.rate = rate
        self.hours = hours

    def accept(self, visitor: EmployeeVisitor):
        return visitor.visit_hourly(self)

class Freelancer(Employee):
    def __init__(self, name, projects, vacation_policy, payment_policy):
        super().__init__(name, "freelancer", vacation_policy, payment_policy)
        self.projects = projects

    def accept(self, visitor: EmployeeVisitor):
        return visitor.visit_freelancer(self)

    def can_request_vacation(self) -> bool:
        return False

class Intern(Employee):
    def __init__(self, name, vacation_policy, payment_policy):
        super().__init__(name, "intern", vacation_policy, payment_policy)

    def accept(self, visitor: EmployeeVisitor):
        return visitor.visit_intern(self)

    def can_request_vacation(self) -> bool:
        return False

# Políticas de pago

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
        employee.log_transaction("payment", total, f"Hourly ({employee.hours} hours) + bonus ${bonus}")  #GOTTA CHECK THIS THING TOO
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

# Políticas de vacaciones

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
    def request_vacation(self, employee, days, payout):  #EVALUAR SI DEBO DEJAR ESTA COSA O NO 
        if employee.vacation_days < days:
            raise Exception("Not enough vacation days.")
        employee.vacation_days -= days
        employee.log_transaction("vacation", days, "Standard vacation/payout")

class FreelancerVacationPolicy(VacationPolicy):
    def request_vacation(self, employee, days, payout):
        raise Exception("Freelancers no pueden tomar vacaciones ni recibir payout.")

# Cargador de configuración

def load_payment_policies_from_json(path="pago.json"):
    with open(path, "r") as f:
        config = json.load(f)
    return {
        "salaried": SalariedPaymentPolicy(config["salaried"]["bonus_percent"]),
        "hourly": HourlyPaymentPolicy(config["hourly"]["bonus_threshold"], config["hourly"]["bonus_amount"]),
        "freelancer": FreelancerPaymentPolicy(),
        "intern": InternPaymentPolicy()
    }
