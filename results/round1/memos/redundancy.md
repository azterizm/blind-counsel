# Advice note: Advise whether an employee is entitled to a statutory redundancy payment under the Employment Rights Act 1996, and how it is calculated.
Date 2026-06-02. Drafted on-device (mlx-community/Qwen3-8B-4bit). Status: ANSWERED WITH FLAGS.

## 1. Was the employee dismissed by their employer within the statutory definition, or are they eligible for a redundancy payment due to lay-off or short-time?
**Answer: YES** [grounded]
Reasoning (on-device model): Tomasz Wisniewski was dismissed by his employer due to redundancy as the Leicester site was closed, and he was not offered a role elsewhere. This falls under the statutory definition of dismissal by reason of redundancy under s135(1)(a) and s136(1) of the Employment Rights Act 1996.
Client facts relied on (verbatim from the account):
  > "On 30 April 2026 he received written notice that the Leicester site would close because the company is moving all printing to its Glasgow site, and that his employment would end on 29 May 2026."
  > "He was not offered a role in Glasgow or anywhere else."
Law relied on (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s135 (sha256 841b18a39b44)
      "An employer shall pay a redundancy payment to any employee of his"
      "is dismissed by the employer by reason of redundancy"
  - uk/ukpga/1996/18/s136 (sha256 0cc7fb89d965)
      "terminated by the employer (whether with or without notice)"
      "terminates by virtue of the limiting event without being renewed under the same contract"

## 2. Was the employee's dismissal wholly or mainly attributable to the employer ceasing or intending to cease business, or to a cessation or diminution of the requirements for employees to carry out work of a particular kind?
**Answer: YES** [grounded]
Reasoning (on-device model): The dismissal of Tomasz Wisniewski is wholly or mainly attributable to the employer ceasing business at the Leicester site, as the employer informed him that the site would close and his employment would end. The closure of the Leicester site and the relocation of operations to Glasgow constitute the business cessation that satisfies the statutory test under s139.
Client facts relied on (verbatim from the account):
  > "On 30 April 2026 he received written notice that the Leicester site would close because the company is moving all printing to its Glasgow site, and that his employment would end on 29 May 2026."
  > "He was not offered a role in Glasgow or anywhere else."
Law relied on (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s139 (sha256 9e63798a292a)
      "wholly or mainly attributable to"
      "the fact that his employer has ceased or intends to cease"

## 3. Can the statutory relevant date of termination be established, including any extension where statutory minimum notice would expire after the standard termination date?
**Answer: UNCLEAR** [ungrounded]
Reasoning (on-device model): Under section 145, the relevant date for statutory redundancy payments is the date on which the notice expires. In this case, the notice from the employer expired on 29 May 2026, which is the relevant date for determining the statutory minimum notice period and the calculation of redundancy payments. Section 145(5) also extends the relevant date if statutory notice under section 86 would have expired later than the standard termination date, which may apply here.
  ! rejected 1 quote(s) not found in the account
Law relied on (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s145 (sha256 e3b1bba03ec1)
      "the date on which the notice expires"
      "the date on which the termination takes effect"
If not met: The statutory relevant date cannot be ascertained, preventing the determination of qualifying service and payment calculation.

## 4. Did the employee have at least two years of continuous employment ending with the relevant date?
**Answer: YES** [grounded]
Reasoning (on-device model): The employee's continuous employment ended on 29 May 2026, which is the relevant date for statutory redundancy purposes. The employee has at least two years of continuous employment ending with this date, meeting the statutory threshold for a redundancy payment.
Client facts relied on (verbatim from the account):
  > "He has worked as a press operator at the Leicester site since 1 March 2017."
  > "his employment would end on 29 May 2026."
Law relied on (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s155 (sha256 fb271294438f)
      "continuously employed for a period of not less than two years"
      "ending with the relevant date"

## 5. Is the amount of the redundancy payment calculated by reckoning backwards from the relevant date up to 20 years of continuous service and applying the prescribed statutory rates based on the employee's age during each year to a week's pay?
**Answer: YES** [grounded]
Reasoning (on-device model): Section 162 of the Employment Rights Act 1996 specifies that the calculation of statutory redundancy payments involves reckoning backwards from the relevant date up to a maximum of 20 years of continuous service, applying statutory rates based on the employee's age during each year. The relevant date for this case is 29 May 2026, as the notice of termination expires on that date. The calculation includes the employee's age during each year of service and applies the appropriate statutory multiplier for each year.
Client facts relied on (verbatim from the account):
  > "He has worked as a press operator at the Leicester site since 1 March 2017."
  > "On 30 April 2026 he received written notice that the Leicester site would close because the company is moving all printing to its Glasgow site, and that his employment would end on 29 May 2026."
Law relied on (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s162 (sha256 0f5ad5a16f88)
      "determining the period, ending with the relevant date, during which the employee has been continuously employed"
      "reckoning backwards from the end of that period the number of years of employment falling within that period"
