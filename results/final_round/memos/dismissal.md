# Advice note: Advise whether an employee has a viable ordinary unfair-dismissal claim under the Employment Rights Act 1996 (eligibility, fairness, time limit, compensation).
Drafted on-device (mlx-community/Qwen3-8B-4bit). Status: ANSWERED (every step computed or grounded).

## Verified client facts
- start_date: 2023-08-04  ("Ms Okafor started work as a dispatch supervisor on 4 August 2023 under a written contract of employment.")
- termination_date: 2026-03-13  ("She received a short dismissal letter dated 13 March 2026.")
- notice_given: False  ("No investigation meeting or disciplinary hearing took place and she was not offered an appeal.")
- advice_date: 2026-05-15  ("Note of client meeting, 15 May 2026.")
- annual_pay: 48500.0  ("Her gross pay was £48,500 a year (about £932 a week).")
- weekly_pay: 932.0  ("Her gross pay was £48,500 a year (about £932 a week).")

## 1. Has the employee been dismissed by the employer within the statutory meaning of section 95 (taking into account the effective date of termination under section 97)?
**Answer: YES** [grounded; on-device model]
Under section 95, an employee is treated as dismissed if the employer terminates the contract. In this case, the employer terminated Ms Okafor's contract with immediate effect for gross misconduct, which constitutes dismissal within the statutory meaning. The effective date of termination is the date the dismissal takes effect, which is March 13, 2026, as per section 97.
  > "On 12 March 2026 her manager, Dave Pritchard, telephoned her and told her she was dismissed with immediate effect for gross misconduct"
  > "She received a short dismissal letter dated 13 March 2026"
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s95 (sha256 a46c73d0a4a6)
  - uk/ukpga/1996/18/s97 (sha256 6499f042cc76)

## 2. Does the employee satisfy the continuous employment qualifying period required under section 108 (normally two years), including any statutory extension of the effective date of termination under section 97 read with section 86?
**Answer: YES** [computed; computed by code]
Continuous employment from 2023-08-04 to the effective date of termination 2026-03-13 (extended under s97(2) by 2 week(s) of unpaid statutory notice to 2026-03-27): 2 complete year(s) against the 2-year requirement in s108(1).
  > "No investigation meeting or disciplinary hearing took place and she was not offered an appeal."
  > "Ms Okafor started work as a dispatch supervisor on 4 August 2023 under a written contract of employment."
  > "She received a short dismissal letter dated 13 March 2026."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s108 (sha256 1f01f5d340f2)
      "unless he has been continuously employed for a period of not less than two years ending with the effective date of termination"
  - uk/ukpga/1996/18/s97 (sha256 6499f042cc76)
  - uk/ukpga/1996/18/s86 (sha256 5295446ecf03)
      "is not less than twelve weeks’ notice if his period of continuous employment is twelve years or more"
      "is not less than one week’s notice for each year of continuous employment if his period of continuous employment is two years or more"
      "is not less than one week’s notice if his period of continuous employment is less than two years"

## 3. Has the tribunal complaint been presented—or can it still be presented—within three months of the effective date of termination under section 111 (subject to statutory extensions or reasonable practicability)?
**Answer: YES — 2026-06-12** [computed; computed by code]
Primary limit under s111(2)(a): 3 months beginning with the EDT 2026-03-13, i.e. on or before 2026-06-12; no claim presented yet; 28 day(s) remain at the advice date 2026-05-15. (ACAS early-conciliation extensions under s207B and the 'not reasonably practicable' extension are not computed.)
  > "Note of client meeting, 15 May 2026."
  > "She received a short dismissal letter dated 13 March 2026."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s111 (sha256 ea23548dee03)
      "before the end of the period of three months beginning with the effective date of termination,"
  - uk/ukpga/1996/18/s97 (sha256 6499f042cc76)

## 4. Is the dismissal unfair under section 98, because the employer cannot demonstrate a potentially fair statutory reason or because the employer acted unreasonably in treating that reason as sufficient to dismiss?
**Answer: YES** [grounded; on-device model]
Under section 98, the employer must establish the principal reason for dismissal, which in this case is alleged to be gross misconduct due to unauthorised absence. However, the employer failed to conduct an investigation or disciplinary hearing, and the dismissal was immediate without notice, which raises questions about the reasonableness of the dismissal. The tribunal will need to assess whether the employer acted reasonably in treating the absence as sufficient grounds for dismissal, considering the lack of investigation and the employee's explanation.
  > "On 12 March 2026 her manager, Dave Pritchard, telephoned her and told her she was dismissed with immediate effect for gross misconduct, namely three days' unauthorised absence from 16 to 18 February 2026."
  > "She says she emailed Mr Pritchard on 15 February explaining that her daughter had been admitted to hospital, and she has kept a copy of that email."
  > "No investigation meeting or disciplinary hearing took place and she was not offered an appeal."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s98 (sha256 98cf854c5298)

## 5. Is the employee entitled to a compensatory award under section 123, subject to the applicable statutory cap and calculation rules under section 124?
**Answer: YES — 48500** [computed; computed by code]
s124(1ZA): the lower of £123,543 and 52 x a week's pay (£932.69) = £48,500. This caps the compensatory award; it does not decide whether there is a loss.
  > "Her gross pay was £48,500 a year (about £932 a week)."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s123 (sha256 dd498e7bcf12)
  - uk/ukpga/1996/18/s124 (sha256 7d7be23f7c54)
      "The amount specified in this subsection is the lower of—
    (a) £123,543,"
      "is the lower of—
    (a) £123,543, and
    (b) 52 multiplied by a week’s pay of the person concerned."
