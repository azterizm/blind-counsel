# Advice note: Advise whether an employee has a viable ordinary unfair-dismissal claim under the Employment Rights Act 1996 (eligibility, fairness, time limit, compensation).
Drafted on-device (mlx-community/Qwen3-8B-4bit). Status: REFER: could not decide enough steps.

## Verified client facts
- advice_date: 2026-09-22  ("Note of client meeting, 22 September 2026.")

## 1. Has the employee been dismissed by the employer within the statutory meaning of section 95 (taking into account the effective date of termination under section 97)?
**Answer: NO** [grounded; on-device model]
The employee has not been dismissed by the employer as defined in section 95. There is no indication that the employer has terminated the contract, the employee has not resigned in response to employer conduct, and there is no evidence of a limited-term contract expiring without renewal. The employee is still employed and has not terminated the contract.
  > "She has not resigned and has not been dismissed."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s95 (sha256 a46c73d0a4a6)

## 2. Does the employee satisfy the continuous employment qualifying period required under section 108 (normally two years), including any statutory extension of the effective date of termination under section 97 read with section 86?
**Answer: UNCLEAR** [unclear; computed by code]
Not computed: missing verified input (start_date).
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s108 (sha256 1f01f5d340f2)
      "unless he has been continuously employed for a period of not less than two years ending with the effective date of termination"
  - uk/ukpga/1996/18/s97 (sha256 6499f042cc76)
  - uk/ukpga/1996/18/s86 (sha256 5295446ecf03)
      "is not less than twelve weeks’ notice if his period of continuous employment is twelve years or more"
      "is not less than one week’s notice for each year of continuous employment if his period of continuous employment is two years or more"
      "is not less than one week’s notice if his period of continuous employment is less than two years"

## 3. Has the tribunal complaint been presented—or can it still be presented—within three months of the effective date of termination under section 111 (subject to statutory extensions or reasonable practicability)?
**Answer: UNCLEAR** [unclear; computed by code]
Not computed: missing verified input (termination_date).
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s111 (sha256 ea23548dee03)
      "before the end of the period of three months beginning with the effective date of termination,"
  - uk/ukpga/1996/18/s97 (sha256 6499f042cc76)

## 4. Is the dismissal unfair under section 98, because the employer cannot demonstrate a potentially fair statutory reason or because the employer acted unreasonably in treating that reason as sufficient to dismiss?
**Answer: UNCLEAR** [unclear; on-device model]
The facts do not establish whether the employer has dismissed Ms Osei or whether the employer has demonstrated a statutory reason for any potential dismissal. The account indicates that she has not been dismissed and is still employed. Therefore, it is unclear whether the dismissal is unfair under section 98.
  > "Ms Osei is still employed as a senior associate."
  > "She has not resigned and has not been dismissed."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s98 (sha256 98cf854c5298)

## 5. Is the employee entitled to a compensatory award under section 123, subject to the applicable statutory cap and calculation rules under section 124?
**Answer: UNCLEAR** [unclear; computed by code]
Not computed: missing verified input (weekly_pay).
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s123 (sha256 dd498e7bcf12)
  - uk/ukpga/1996/18/s124 (sha256 7d7be23f7c54)
      "The amount specified in this subsection is the lower of—
    (a) £123,543,"
      "is the lower of—
    (a) £123,543, and
    (b) 52 multiplied by a week’s pay of the person concerned."
