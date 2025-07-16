
import os
from dataclasses import dataclass
from typing import List

FIXED_VACATION_DAYS_PAYOUT = 5  # The fixed nr of vacation days that can be paid out.


@dataclass
class Employee:
    """Basic representation of an employee at the company."""

    name: str
    role: str
    vacation_days: int = 25

    def take_a_holiday(self, payout: bool) -> None:
        """Let the employee take a single holiday, or pay out 5 holidays."""
        if payout:
            # check that there are enough vacation days left for a payout
            if self.vacation_days < FIXED_VACATION_DAYS_PAYOUT:
                raise ValueError(
                    f"You don't have enough holidays left over for a payout.\
                        Remaining holidays: {self.vacation_days}."
                )
            try:
                self.vacation_days -= FIXED_VACATION_DAYS_PAYOUT
                print(f"Paying out a holiday. Holidays left: {self.vacation_days}")
            except Exception:
                # this should never happen
                pass
        else:
            if self.vacation_days < 1:
                raise ValueError(
                    "You don't have any holidays left. Now back to work, you!"
                )
            self.vacation_days -= 1
            print("Have fun on your holiday. Don't forget to check your emails!")


@dataclass
class HourlyEmployee(Employee):
    """Employee that's paid based on number of worked hours."""

    hourly_rate: float = 50
    amount: int = 10


@dataclass
class SalariedEmployee(Employee):
    """Employee that's paid based on a fixed monthly salary."""

    monthly_salary: float = 5000


class Company:
    """Represents a company with employees."""

    def __init__(self) -> None:
        self.employees: List[Employee] = []

    def add_employee(self, employee: Employee) -> None:
        """Add an employee to the list of employees."""
        self.employees.append(employee)

    def find_managers(self) -> List[Employee]:
        """Find all manager employees."""
        managers = []
        for employee in self.employees:
            if employee.role == "manager":
                managers.append(employee)
        return managers

    def find_vice_presidents(self) -> List[Employee]:
        """Find all vice-president employees."""
        vice_presidents = []
        for employee in self.employees:
            if employee.role == "vice_president":
                vice_presidents.append(employee)
        return vice_presidents

    def find_interns(self) -> List[Employee]:
        """Find all interns."""
        interns = []
        for employee in self.employees:
            if employee.role == "intern":
                interns.append(employee)
        return interns

    def pay_employee(self, employee: Employee) -> None:
        """Pay an employee."""
        if isinstance(employee, SalariedEmployee):
            print(
                f"Paying employee {employee.name} a monthly salary of ${employee.monthly_salary}."
            )
        elif isinstance(employee, HourlyEmployee):
            print(
                f"Paying employee {employee.name} a hourly rate of ${employee.hourly_rate*employee.amount}"
            )


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main(): #-----------------------------Tis is the main function-----------------------------------
    #It helps to manage the employee management system.
    company = Company()

    while True:
        clear_screen()
        print("--- Employee Management Menu ---")
        print("1. Create employee")
        print("2. View employees")
        print("3. Grant vacation to an employee")
        print("4. Pay employees")
        print("5. Exit")

        choice = input("Select an option: ")

        if choice == "1":
            name = input("Employee name: ")
            role = input("Role (intern, manager, vice_president): ").lower()
            emp_type = input("Employee type (salaried/hourly): ").lower()

            if emp_type == "salaried":
                try:
                    salary = float(input("Monthly salary: "))
                    employee = SalariedEmployee(name=name, role=role, monthly_salary=salary)
                except ValueError:
                    print("Invalid salary input.")
                    input("Press Enter to continue...")
                    continue
            elif emp_type == "hourly":
                try:
                    rate = float(input("Hourly rate: "))
                    hours = int(input("Hours worked: "))
                    employee = HourlyEmployee(name=name, role=role, hourly_rate=rate, amount=hours)
                except ValueError:
                    print("Invalid hourly input.")
                    input("Press Enter to continue...")
                    continue
            else:
                print("Invalid employee type.")
                input("Press Enter to continue...")
                continue

            company.add_employee(employee)
            print("Employee created successfully.")
            input("Press Enter to continue...")

        elif choice == "2":
            while True:
                clear_screen() #establishes a clear screen for better visibility
                print("--- View Employees Submenu ---")
                print("1. View managers")
                print("2. View interns")#this is used to view the interns
                print("3. View vice presidents")
                print("0. Return to main menu")

                sub_choice = input("Select an option: ")

                if sub_choice == "1":
                    managers = company.find_managers()
                    for emp in managers:
                        print(f"{emp.name} ({emp.role}) - {emp.vacation_days} vacation days")
                elif sub_choice == "2":
                    interns = company.find_interns()
                    for emp in interns:
                        print(f"{emp.name} ({emp.role}) - {emp.vacation_days} vacation days")
                elif sub_choice == "3":
                    vps = company.find_vice_presidents()
                    for emp in vps:
                        print(f"{emp.name} ({emp.role}) - {emp.vacation_days} vacation days")
                elif sub_choice == "0":
                    break
                else:
                    print("Invalid option.")
                input("Press Enter to continue...")

        elif choice == "3":
            clear_screen()
            if not company.employees:
                print("No employees available.")
                input("Press Enter to continue...")
                continue

            for idx, emp in enumerate(company.employees):
                print(f"{idx}. {emp.name} ({emp.role}) - {emp.vacation_days} vacation days")
            try:
                idx = int(input("Select employee index: "))
                payout = input("Payout instead of time off? (y/n): ").lower() == "y"
                company.employees[idx].take_a_holiday(payout)
            except (IndexError, ValueError) as e:
                print(f"Error: {e}")
            input("Press Enter to continue...")

        elif choice == "4":
            clear_screen()
            for emp in company.employees:
                company.pay_employee(emp)
            input("Press Enter to continue...")

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid option.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()