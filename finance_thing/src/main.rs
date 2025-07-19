use std::fmt;

struct InvestmentPlan {
    initial: f64,
    monthly_contribution: f64,
    annual_interest_rate: f64, // e.g., 1.05 for 5%
}

#[derive(Debug)]
struct YearlyReport {
    year: i32,
    yearly_contribution: f64,
    interest_earned: f64,
    total_value: f64,
}

impl fmt::Display for YearlyReport {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "Year {}: Contributions = ${:.2}, Interest = ${:.2}, Total = ${:.2}",
            self.year, self.yearly_contribution, self.interest_earned, self.total_value
        )
    }
}

impl InvestmentPlan {
    fn evolve(&mut self, year:i32) -> YearlyReport {
        let mut balance = self.initial;
        let monthly_rate = (self.annual_interest_rate-1.0) / 12.0;
        let mut yearly_contribution = 0.0;

        let start_balance = balance;

        for _ in 0..12 {
            balance *= 1.0 + monthly_rate;
            balance += self.monthly_contribution;
            yearly_contribution += self.monthly_contribution;
        }

        let interest_earned = balance - start_balance - yearly_contribution;
        
        // Update the state
        self.initial = balance;

        YearlyReport {
            year,
            yearly_contribution,
            interest_earned,
            total_value: balance,
        }
    }
}

fn main() {
    // Configure investment plan trajectory.
    let salary_increase_rate = 1.04;
    let mut monthly_contribution = 1000.0;

    // Setup the market and model.
    let mut plan = InvestmentPlan {
        initial: 1000.0,
        monthly_contribution: monthly_contribution,
        annual_interest_rate: 1.13,
    };

    // Integrate the model
    let n_years:i32 = 20;
    for year in 1..=n_years {
        let report = plan.evolve(year);

        // Update the monthly contributions.
        monthly_contribution *= salary_increase_rate;
        plan.monthly_contribution=monthly_contribution;
        println!("{}", report);
    }
}
