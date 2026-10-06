# Advice note: Advise whether an employee is entitled to a statutory redundancy payment under the Employment Rights Act 1996, and how it is calculated.
Drafted on-device (mlx-community/Qwen3-8B-4bit). Status: ANSWERED (every step computed or grounded).

## Verified client facts
- start_date: 2025-01-04  ("Mr Reyes worked as a machine operator from 4 January 2025.")
- termination_date: 2026-08-14  ("ending on 14 August 2026.")
- notice_given: True  ("the company told him the print room was closing and gave him one week's notice of dismissal for redundancy")
- notice_given_date: 2026-08-07  ("On 7 August 2026 the company told him the print room was closing and gave him one week's notice of dismissal for redundancy")
- advice_date: 2026-09-10  ("Note of client meeting, 10 September 2026.")
- weekly_pay: 520.0  ("His gross weekly pay was £520.")
- age: 27  ("Client: Daniel Reyes, aged 27.")
- (1 extracted fact(s) rejected: not literally in the account)

## 1. Has the employee been dismissed by the employer within the statutory definition under section 136?
**Answer: YES** [grounded; on-device model]
The employee was dismissed by the employer due to redundancy as the employer informed him of the print room closure and gave one week's notice of dismissal, which falls under the statutory definition of dismissal by reason of redundancy under section 136. The redundancy payment is triggered under section 135.
  > "On 7 August 2026 the company told him the print room was closing and gave him one week's notice of dismissal for redundancy, ending on 14 August 2026."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s135 (sha256 841b18a39b44)
  - uk/ukpga/1996/18/s136 (sha256 0cc7fb89d965)

## 2. Is the dismissal wholly or mainly attributable to the employer ceasing or intending to cease business (either entirely or where the employee worked) or to diminished requirements for employees to carry out work of a particular kind?
**Answer: YES** [grounded; on-device model]
The dismissal is wholly or mainly attributable to the employer ceasing business, as the print room was closed, and the notice of dismissal was given for redundancy. The statutory test in section 139(1) is satisfied as the employer's business ceased in the place where the employee was employed.
  > "On 7 August 2026 the company told him the print room was closing and gave him one week's notice of dismissal for redundancy, ending on 14 August 2026."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s139 (sha256 9e63798a292a)

## 3. Has the statutory relevant date of dismissal been determined, incorporating any extension required by section 86 statutory minimum notice?
**Answer: YES — 2026-08-14** [computed; computed by code]
Relevant date under s145(2): 2026-08-14.
  > "the company told him the print room was closing and gave him one week's notice of dismissal for redundancy"
  > "On 7 August 2026 the company told him the print room was closing and gave him one week's notice of dismissal for redundancy"
  > "Mr Reyes worked as a machine operator from 4 January 2025."
  > "ending on 14 August 2026."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s145 (sha256 e3b1bba03ec1)
  - uk/ukpga/1996/18/s86 (sha256 5295446ecf03)
      "is not less than twelve weeks’ notice if his period of continuous employment is twelve years or more"
      "is not less than one week’s notice for each year of continuous employment if his period of continuous employment is two years or more"
      "is not less than one week’s notice if his period of continuous employment is less than two years"

## 4. Did the employee have at least two years of continuous employment ending with the relevant date?
**Answer: NO** [computed; computed by code]
1 complete year(s) of continuous employment ending with the relevant date 2026-08-14 against the 2-year requirement in s155.
  > "the company told him the print room was closing and gave him one week's notice of dismissal for redundancy"
  > "On 7 August 2026 the company told him the print room was closing and gave him one week's notice of dismissal for redundancy"
  > "Mr Reyes worked as a machine operator from 4 January 2025."
  > "ending on 14 August 2026."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s155 (sha256 fb271294438f)
      "continuously employed for a period of not less than two years ending with the relevant date"
  - uk/ukpga/1996/18/s145 (sha256 e3b1bba03ec1)
  - uk/ukpga/1996/18/s86 (sha256 5295446ecf03)
      "is not less than twelve weeks’ notice if his period of continuous employment is twelve years or more"
      "is not less than one week’s notice for each year of continuous employment if his period of continuous employment is two years or more"
      "is not less than one week’s notice if his period of continuous employment is less than two years"

## 5. Has the redundancy payment been calculated in accordance with the statutory rules by reckoning backwards up to 20 years of service and applying the weekly pay cap?
**Answer: NO — 0** [computed; computed by code]
No entitlement under s155, so no payment.
  > "Client: Daniel Reyes, aged 27."
  > "the company told him the print room was closing and gave him one week's notice of dismissal for redundancy"
  > "On 7 August 2026 the company told him the print room was closing and gave him one week's notice of dismissal for redundancy"
  > "Mr Reyes worked as a machine operator from 4 January 2025."
  > "ending on 14 August 2026."
  > "His gross weekly pay was £520."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s162 (sha256 0f5ad5a16f88)
      "one week’s pay for a year of employment (not within paragraph (a)) in which he was not below the age of twenty-two"
      "one and a half weeks’ pay for a year of employment in which the employee was not below the age of forty-one"
      "Where twenty years of employment have been reckoned under subsection (1), no account shall be taken under that subsection"
      "half a week’s pay for each year of employment not within paragraph (a) or (b)"
      "one week’s pay for a year of employment (not within paragraph (a)) in which he was not below the age of twenty-two"
      "one and a half weeks’ pay for a year of employment in which the employee was not below the age of forty-one"
  - uk/ukpga/1996/18/s227 (sha256 7d88f0b178c8)
      "(c) a redundancy payment,
  the amount of a week’s pay shall not exceed £751."
