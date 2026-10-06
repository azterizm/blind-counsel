# Advice note: Advise whether an employee is entitled to a statutory redundancy payment under the Employment Rights Act 1996, and how it is calculated.
Drafted on-device (mlx-community/Qwen3-8B-4bit). Status: ANSWERED (every step computed or grounded).

## Verified client facts
- start_date: 2020-07-01  ("Ms Mensah worked as a store supervisor from 1 July 2020")
- termination_date: 2026-07-31  ("her employment ended on 31 July 2026")
- notice_given: True  ("On 3 July 2026 she was given written notice that her store would close and that her job would end on 31 July 2026")
- notice_given_date: 2026-07-03  ("On 3 July 2026 she was given written notice that her store would close and that her job would end on 31 July 2026")
- advice_date: 2026-08-14  ("Note of client meeting, 14 August 2026")
- weekly_pay: 500.0  ("Her gross weekly pay was £500")
- age: 30  ("Client: Grace Mensah, aged 30")
- (1 extracted fact(s) rejected: not literally in the account)

## 1. Has the employee been dismissed by the employer within the statutory definition under section 136?
**Answer: YES** [grounded; on-device model]
The employee was dismissed by the employer due to redundancy as the store closure was the reason for the termination of her employment. Section 136 of the Employment Rights Act 1996 defines dismissal as the termination of the employment contract by the employer, which applies in this case. The statutory definition of dismissal under section 136 includes situations where the employer terminates the contract, which is the case here.
  > "On 3 July 2026 she was given written notice that her store would close and that her job would end on 31 July 2026; her employment ended on 31 July 2026."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s135 (sha256 841b18a39b44)
  - uk/ukpga/1996/18/s136 (sha256 0cc7fb89d965)

## 2. Is the dismissal wholly or mainly attributable to the employer ceasing or intending to cease business (either entirely or where the employee worked) or to diminished requirements for employees to carry out work of a particular kind?
**Answer: YES** [grounded; on-device model]
The dismissal is wholly or mainly attributable to the employer ceasing business as the store was closed, which meets the criteria under section 139 of the Employment Rights Act 1996. The notice of closure and the termination date align with the statutory definition of redundancy.
  > "On 3 July 2026 she was given written notice that her store would close and that her job would end on 31 July 2026; her employment ended on 31 July 2026."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s139 (sha256 9e63798a292a)

## 3. Has the statutory relevant date of dismissal been determined, incorporating any extension required by section 86 statutory minimum notice?
**Answer: YES — 2026-07-31** [computed; computed by code]
Relevant date under s145(2): 2026-07-31; for ss.155 and 162 it is extended under s145(5) to 2026-08-14 (6 weeks' statutory notice).
  > "On 3 July 2026 she was given written notice that her store would close and that her job would end on 31 July 2026"
  > "On 3 July 2026 she was given written notice that her store would close and that her job would end on 31 July 2026"
  > "Ms Mensah worked as a store supervisor from 1 July 2020"
  > "her employment ended on 31 July 2026"
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s145 (sha256 e3b1bba03ec1)
  - uk/ukpga/1996/18/s86 (sha256 5295446ecf03)
      "is not less than twelve weeks’ notice if his period of continuous employment is twelve years or more"
      "is not less than one week’s notice for each year of continuous employment if his period of continuous employment is two years or more"
      "is not less than one week’s notice if his period of continuous employment is less than two years"

## 4. Did the employee have at least two years of continuous employment ending with the relevant date?
**Answer: YES** [computed; computed by code]
6 complete year(s) of continuous employment ending with the relevant date 2026-08-14 against the 2-year requirement in s155.
  > "On 3 July 2026 she was given written notice that her store would close and that her job would end on 31 July 2026"
  > "On 3 July 2026 she was given written notice that her store would close and that her job would end on 31 July 2026"
  > "Ms Mensah worked as a store supervisor from 1 July 2020"
  > "her employment ended on 31 July 2026"
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s155 (sha256 fb271294438f)
      "continuously employed for a period of not less than two years ending with the relevant date"
  - uk/ukpga/1996/18/s145 (sha256 e3b1bba03ec1)
  - uk/ukpga/1996/18/s86 (sha256 5295446ecf03)
      "is not less than twelve weeks’ notice if his period of continuous employment is twelve years or more"
      "is not less than one week’s notice for each year of continuous employment if his period of continuous employment is two years or more"
      "is not less than one week’s notice if his period of continuous employment is less than two years"

## 5. Has the redundancy payment been calculated in accordance with the statutory rules by reckoning backwards up to 20 years of service and applying the weekly pay cap?
**Answer: YES — 3000.0** [computed; computed by code]
6 year(s) reckoned back from 2026-08-14: 6 weeks' pay x £500.00 (week's pay capped at £751 by s227) = £3,000.00. Ages per year are inferred from the stated age (date of birth not given).
  > "Client: Grace Mensah, aged 30"
  > "On 3 July 2026 she was given written notice that her store would close and that her job would end on 31 July 2026"
  > "On 3 July 2026 she was given written notice that her store would close and that her job would end on 31 July 2026"
  > "Ms Mensah worked as a store supervisor from 1 July 2020"
  > "her employment ended on 31 July 2026"
  > "Her gross weekly pay was £500"
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
