# Advice note: Advise whether an employee has a viable ordinary unfair-dismissal claim under the Employment Rights Act 1996 (eligibility, fairness, time limit, compensation).
Drafted on-device (mlx-community/Qwen3-8B-4bit). Status: ANSWERED WITH FLAGS.

## Verified client facts
- start_date: 2024-03-02  ("Mr Bell started work as a QA engineer on 2 March 2024.")
- termination_date: 2026-08-07  ("his employment ended when that notice expired on 7 August 2026.")
- notice_given: True  ("On 10 July 2026 he was given four weeks' notice of dismissal for alleged poor performance")
- advice_date: 2026-09-09  ("Note of client meeting, 9 September 2026.")
- annual_pay: 41600.0  ("His salary was £41,600 a year.")
- (2 extracted fact(s) rejected: not literally in the account)

## 1. Has the employee been dismissed by the employer within the statutory meaning of section 95 (taking into account the effective date of termination under section 97)?
**Answer: YES** [grounded; on-device model]
The employee was dismissed by the employer within the statutory meaning of section 95 as the employer terminated the contract with notice. Section 95(1)(a) applies as the employer gave notice to terminate the contract of employment, which is consistent with the facts provided.
  > "On 10 July 2026 he was given four weeks' notice of dismissal for alleged poor performance, and his employment ended when that notice expired on 7 August 2026."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s95 (sha256 a46c73d0a4a6)

## 2. Does the employee satisfy the continuous employment qualifying period required under section 108 (normally two years), including any statutory extension of the effective date of termination under section 97 read with section 86?
**Answer: YES** [computed; computed by code]
Continuous employment from 2024-03-02 to the effective date of termination 2026-08-07 (extended under s97(2) by 2 week(s) of unpaid statutory notice to 2026-08-21): 2 complete year(s) against the 2-year requirement in s108(1).
  > "On 10 July 2026 he was given four weeks' notice of dismissal for alleged poor performance"
  > "Mr Bell started work as a QA engineer on 2 March 2024."
  > "his employment ended when that notice expired on 7 August 2026."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s108 (sha256 1f01f5d340f2)
      "unless he has been continuously employed for a period of not less than two years ending with the effective date of termination"
  - uk/ukpga/1996/18/s97 (sha256 6499f042cc76)
  - uk/ukpga/1996/18/s86 (sha256 5295446ecf03)
      "is not less than twelve weeks’ notice if his period of continuous employment is twelve years or more"
      "is not less than one week’s notice for each year of continuous employment if his period of continuous employment is two years or more"
      "is not less than one week’s notice if his period of continuous employment is less than two years"

## 3. Has the tribunal complaint been presented—or can it still be presented—within three months of the effective date of termination under section 111 (subject to statutory extensions or reasonable practicability)?
**Answer: YES — 2026-11-06** [computed; computed by code]
Primary limit under s111(2)(a): 3 months beginning with the EDT 2026-08-07, i.e. on or before 2026-11-06; no claim presented yet; 58 day(s) remain at the advice date 2026-09-09. (ACAS early-conciliation extensions under s207B and the 'not reasonably practicable' extension are not computed.)
  > "Note of client meeting, 9 September 2026."
  > "his employment ended when that notice expired on 7 August 2026."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s111 (sha256 ea23548dee03)
      "before the end of the period of three months beginning with the effective date of termination,"
  - uk/ukpga/1996/18/s97 (sha256 6499f042cc76)

## 4. Is the dismissal unfair under section 98, because the employer cannot demonstrate a potentially fair statutory reason or because the employer acted unreasonably in treating that reason as sufficient to dismiss?
**Answer: UNCLEAR** [unclear; on-device model]
The employer must establish the principal reason for dismissal, which must fall within a statutory category or be a substantial reason. The account does not specify the reason for dismissal, only that it was for 'alleged poor performance.' The tribunal would need to determine if this reason is sufficient and if the employer acted reasonably. The employer's size and administrative resources are also relevant to the reasonableness test under section 98(4).
  > "On 10 July 2026 he was given four weeks' notice of dismissal for alleged poor performance"
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s98 (sha256 98cf854c5298)

## 5. Is the employee entitled to a compensatory award under section 123, subject to the applicable statutory cap and calculation rules under section 124?
**Answer: YES — 41600** [computed; computed by code]
s124(1ZA): the lower of £123,543 and 52 x a week's pay (£800.00) = £41,600. This caps the compensatory award; it does not decide whether there is a loss.
  > "His salary was £41,600 a year."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s123 (sha256 dd498e7bcf12)
  - uk/ukpga/1996/18/s124 (sha256 7d7be23f7c54)
      "The amount specified in this subsection is the lower of—
    (a) £123,543,"
      "is the lower of—
    (a) £123,543, and
    (b) 52 multiplied by a week’s pay of the person concerned."
