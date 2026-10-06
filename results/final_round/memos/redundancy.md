# Advice note: Advise whether an employee is entitled to a statutory redundancy payment under the Employment Rights Act 1996, and how it is calculated.
Drafted on-device (mlx-community/Qwen3-8B-4bit). Status: ANSWERED (every step computed or grounded).

## Verified client facts
- start_date: 2017-03-01  ("He has worked as a press operator at the Leicester site since 1 March 2017.")
- termination_date: 2026-05-29  ("his employment would end on 29 May 2026.")
- notice_given: True  ("On 30 April 2026 he received written notice that the Leicester site would close...")
- notice_given_date: 2026-04-30  ("On 30 April 2026 he received written notice that the Leicester site would close...")
- weekly_pay: 610.0  ("His gross weekly pay was £610.")
- age: 44  ("Client: Tomasz Wisniewski, aged 44.")
- (1 extracted fact(s) rejected: not literally in the account)

## 1. Has the employee been dismissed by the employer within the statutory definition under section 136?
**Answer: YES** [grounded; on-device model]
Under section 136, an employee is dismissed if the employer terminates the contract, which includes the closure of the Leicester site. The employee was informed his employment would end on 29 May 2026 due to redundancy, which meets the statutory definition of dismissal by reason of redundancy under section 135(1)(a).
  > "On 30 April 2026 he received written notice that the Leicester site would close because the company is moving all printing to its Glasgow site, and that his employment would end on 29 May 2026."
  > "He was not offered a role in Glasgow or anywhere else."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s135 (sha256 841b18a39b44)
  - uk/ukpga/1996/18/s136 (sha256 0cc7fb89d965)

## 2. Is the dismissal wholly or mainly attributable to the employer ceasing or intending to cease business (either entirely or where the employee worked) or to diminished requirements for employees to carry out work of a particular kind?
**Answer: YES** [grounded; on-device model]
The dismissal is wholly or mainly attributable to the employer ceasing business at the Leicester site, as the employer informed Tomasz Wisniewski that the site would close and his employment would end due to the company moving operations to Glasgow. This aligns with the statutory definition in section 139 of the Employment Rights Act 1996, which includes business closure as a redundancy reason.
  > "On 30 April 2026 he received written notice that the Leicester site would close because the company is moving all printing to its Glasgow site, and that his employment would end on 29 May 2026."
  > "He was not offered a role in Glasgow or anywhere else."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s139 (sha256 9e63798a292a)

## 3. Has the statutory relevant date of dismissal been determined, incorporating any extension required by section 86 statutory minimum notice?
**Answer: YES — 2026-05-29** [computed; computed by code]
Relevant date under s145(2): 2026-05-29; for ss.155 and 162 it is extended under s145(5) to 2026-07-02 (9 weeks' statutory notice).
  > "On 30 April 2026 he received written notice that the Leicester site would close..."
  > "On 30 April 2026 he received written notice that the Leicester site would close..."
  > "He has worked as a press operator at the Leicester site since 1 March 2017."
  > "his employment would end on 29 May 2026."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s145 (sha256 e3b1bba03ec1)
  - uk/ukpga/1996/18/s86 (sha256 5295446ecf03)
      "is not less than twelve weeks’ notice if his period of continuous employment is twelve years or more"
      "is not less than one week’s notice for each year of continuous employment if his period of continuous employment is two years or more"
      "is not less than one week’s notice if his period of continuous employment is less than two years"

## 4. Did the employee have at least two years of continuous employment ending with the relevant date?
**Answer: YES** [computed; computed by code]
9 complete year(s) of continuous employment ending with the relevant date 2026-07-02 against the 2-year requirement in s155.
  > "On 30 April 2026 he received written notice that the Leicester site would close..."
  > "On 30 April 2026 he received written notice that the Leicester site would close..."
  > "He has worked as a press operator at the Leicester site since 1 March 2017."
  > "his employment would end on 29 May 2026."
Law (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s155 (sha256 fb271294438f)
      "continuously employed for a period of not less than two years ending with the relevant date"
  - uk/ukpga/1996/18/s145 (sha256 e3b1bba03ec1)
  - uk/ukpga/1996/18/s86 (sha256 5295446ecf03)
      "is not less than twelve weeks’ notice if his period of continuous employment is twelve years or more"
      "is not less than one week’s notice for each year of continuous employment if his period of continuous employment is two years or more"
      "is not less than one week’s notice if his period of continuous employment is less than two years"

## 5. Has the redundancy payment been calculated in accordance with the statutory rules by reckoning backwards up to 20 years of service and applying the weekly pay cap?
**Answer: YES — 6405.0** [computed; computed by code]
9 year(s) reckoned back from 2026-07-02: 10.5 weeks' pay x £610.00 (week's pay capped at £751 by s227) = £6,405.00. Ages per year are inferred from the stated age (date of birth not given).
  > "Client: Tomasz Wisniewski, aged 44."
  > "On 30 April 2026 he received written notice that the Leicester site would close..."
  > "On 30 April 2026 he received written notice that the Leicester site would close..."
  > "He has worked as a press operator at the Leicester site since 1 March 2017."
  > "his employment would end on 29 May 2026."
  > "His gross weekly pay was £610."
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
