# Advice note: Advise whether an employee has a viable ordinary unfair-dismissal claim under the Employment Rights Act 1996 (eligibility, fairness, time limit, compensation).
Drafted on-device (mlx-community/Qwen3-8B-4bit). Status: ANSWERED WITH FLAGS.

## Verified client facts
- start_date: 2019-01-14  ("Ms Siddiqui worked as a transport planner from 14 January 2019.")
- termination_date: 2026-02-02  ("She was dismissed with immediate effect on 2 February 2026 for alleged gross misconduct.")
- notice_given: False  ("She was dismissed with immediate effect on 2 February 2026 for alleged gross misconduct.")
- advice_date: 2026-05-05  ("Note of client meeting, 5 May 2026.")
- annual_pay: 45500.0  ("Her salary was £45,500 a year.")
- (1 extracted fact(s) rejected: not literally in the account)

## 1. Has the employee been dismissed by the employer within the statutory meaning of section 95 (taking into account the effective date of termination under section 97)?
**Answer: YES** [grounded; on-device model]
Under section 95, an employee is treated as dismissed if the employer terminates the contract. The employee was dismissed with immediate effect on 2 February 2026, which constitutes the employer terminating the contract. Section 97 defines the effective date of termination, which in this case is the date the dismissal takes effect, as the employer did not give notice.
  > "She was dismissed with immediate effect on 2 February 2026 for alleged gross misconduct."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s95 (sha256 a46c73d0a4a6)

## 2. Does the employee satisfy the continuous employment qualifying period required under section 108 (normally two years), including any statutory extension of the effective date of termination under section 97 read with section 86?
**Answer: YES** [computed; computed by code]
Continuous employment from 2019-01-14 to the effective date of termination 2026-02-02 (extended under s97(2) by 7 week(s) of unpaid statutory notice to 2026-03-23): 7 complete year(s) against the 2-year requirement in s108(1).
  > "She was dismissed with immediate effect on 2 February 2026 for alleged gross misconduct."
  > "Ms Siddiqui worked as a transport planner from 14 January 2019."
  > "She was dismissed with immediate effect on 2 February 2026 for alleged gross misconduct."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s108 (sha256 1f01f5d340f2)
      "unless he has been continuously employed for a period of not less than two years ending with the effective date of termination"
  - uk/ukpga/1996/18/s97 (sha256 6499f042cc76)
  - uk/ukpga/1996/18/s86 (sha256 5295446ecf03)
      "is not less than twelve weeks’ notice if his period of continuous employment is twelve years or more"
      "is not less than one week’s notice for each year of continuous employment if his period of continuous employment is two years or more"
      "is not less than one week’s notice if his period of continuous employment is less than two years"

## 3. Has the tribunal complaint been presented—or can it still be presented—within three months of the effective date of termination under section 111 (subject to statutory extensions or reasonable practicability)?
**Answer: NO — 2026-05-01** [computed; computed by code]
Primary limit under s111(2)(a): 3 months beginning with the EDT 2026-02-02, i.e. on or before 2026-05-01; no claim presented and the deadline passed 4 day(s) before the advice date 2026-05-05. (ACAS early-conciliation extensions under s207B and the 'not reasonably practicable' extension are not computed.)
  > "Note of client meeting, 5 May 2026."
  > "She was dismissed with immediate effect on 2 February 2026 for alleged gross misconduct."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s111 (sha256 ea23548dee03)
      "before the end of the period of three months beginning with the effective date of termination,"
  - uk/ukpga/1996/18/s97 (sha256 6499f042cc76)

## 4. Is the dismissal unfair under section 98, because the employer cannot demonstrate a potentially fair statutory reason or because the employer acted unreasonably in treating that reason as sufficient to dismiss?
**Answer: UNCLEAR** [unclear; on-device model]
Section 98 of the Employment Rights Act 1996 requires the employer to establish the principal reason for dismissal and demonstrate that it falls within a statutory category or is a substantial reason. The employer must also show that they acted reasonably in treating that reason as sufficient. However, the provided information does not specify the reason for dismissal or whether it falls within a statutory category. Therefore, it is unclear if the dismissal was fair or unfair under section 98.
  ! rejected 1 quote(s) not found in the account
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s98 (sha256 98cf854c5298)

## 5. Is the employee entitled to a compensatory award under section 123, subject to the applicable statutory cap and calculation rules under section 124?
**Answer: YES — 45500** [computed; computed by code]
s124(1ZA): the lower of £123,543 and 52 x a week's pay (£875.00) = £45,500. This caps the compensatory award; it does not decide whether there is a loss.
  > "Her salary was £45,500 a year."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s123 (sha256 dd498e7bcf12)
  - uk/ukpga/1996/18/s124 (sha256 7d7be23f7c54)
      "The amount specified in this subsection is the lower of—
    (a) £123,543,"
      "is the lower of—
    (a) £123,543, and
    (b) 52 multiplied by a week’s pay of the person concerned."
