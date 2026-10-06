# Advice note: Advise whether an employee has a viable ordinary unfair-dismissal claim under the Employment Rights Act 1996 (eligibility, fairness, time limit, compensation).
Date 2026-05-15. Drafted on-device (mlx-community/Qwen3-8B-4bit). Status: ANSWERED (all conclusions grounded).

## 1. Is the individual an employee who has been dismissed by their employer within the meaning of section 95?
**Answer: YES** [grounded]
Reasoning (on-device model): The individual is treated as dismissed under section 95 as the employer terminated her contract with immediate effect for gross misconduct. Section 95(1) provides that dismissal occurs where the employer terminates the contract, which is the case here. The effective date of termination is the date the dismissal takes effect, which is 13 March 2026, as per section 97.
Client facts relied on (verbatim from the account):
  > "On 12 March 2026 her manager, Dave Pritchard, telephoned her and told her she was dismissed with immediate effect for gross misconduct"
  > "She received a short dismissal letter dated 13 March 2026"
Law relied on (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s95 (sha256 a46c73d0a4a6)
      "the contract under which he is employed is terminated by the employer (whether with or without notice)"
      "he is employed under a limited-term contract and that contract terminates by virtue of the limiting event without being renewed under the same contract"
  - uk/ukpga/1996/18/s97 (sha256 6499f042cc76)
      "means the date on which the notice expires"
      "means the date on which the termination takes effect"

## 2. Does the employee have the requisite period of continuous employment to qualify for unfair dismissal protection?
**Answer: NO** [grounded]
Reasoning (on-device model): The employee has not completed the two-year continuous employment period required for unfair dismissal protection. The effective date of termination is 13 March 2026, and the employee started work on 4 August 2023, resulting in less than two years of continuous service. The dismissal was for gross misconduct, which does not fall under the statutory exceptions that would reduce the qualifying period.
Client facts relied on (verbatim from the account):
  > "Ms Okafor started work as a dispatch supervisor on 4 August 2023"
  > "On 12 March 2026 her manager, Dave Pritchard, telephoned her and told her she was dismissed with immediate effect"
  > "She says she emailed Mr Pritchard on 15 February explaining that her daughter had been admitted to hospital"
Law relied on (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s108 (sha256 1f01f5d340f2)
      "continuously employed for a period of not less than two years ending with the effective date of termination"
      "dismissed by reason of any such requirement or recommendation as is referred to in section 64(2)"
  - uk/ukpga/1996/18/s97 (sha256 6499f042cc76)
      "means the date on which the notice expires"
      "means the date on which the termination takes effect"
If not met: The employee is excluded under section 108(1) from bringing an ordinary unfair dismissal claim.

## 3. Was the complaint presented to an employment tribunal within three months of the effective date of termination (or within an allowable extended period)?
**Answer: NO** [grounded]
Reasoning (on-device model): The effective date of termination was 13 March 2026, as the dismissal was with immediate effect. The complaint was not presented to the employment tribunal within three months of this date, and there is no indication that the complaint was submitted within a reasonable time thereafter or that there were statutory conciliation extensions applicable.
Client facts relied on (verbatim from the account):
  > "On 12 March 2026 her manager, Dave Pritchard, telephoned her and told her she was dismissed with immediate effect for gross misconduct"
  > "She has not yet contacted ACAS or presented a claim to an employment tribunal"
Law relied on (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s111 (sha256 ea23548dee03)
      "A complaint may be presented to an employment tribunal against an employer by any person that he was unfairly dismissed by the employer."
      "before the end of the period of three months beginning with the effective date of termination"
  - uk/ukpga/1996/18/s97 (sha256 6499f042cc76)
      "means the date on which the notice expires"
      "means the date on which the termination takes effect"
If not met: The tribunal will lack jurisdiction to hear the complaint under section 111.

## 4. Did the employer fail to establish a potentially fair reason for the dismissal, or act unreasonably in treating that reason as sufficient to dismiss?
**Answer: YES** [grounded]
Reasoning (on-device model): The employer failed to establish a potentially fair reason for the dismissal as the principal reason was gross misconduct, which requires a fair procedure. The employer did not conduct an investigation or offer a disciplinary hearing, which is necessary to demonstrate fairness under the statutory test. The dismissal was not supported by a fair process, making the reason for dismissal unclear and potentially unfair.
Client facts relied on (verbatim from the account):
  > "On 12 March 2026 her manager, Dave Pritchard, telephoned her and told her she was dismissed with immediate effect for gross misconduct, namely three days' unauthorised absence from 16 to 18 February 2026."
  > "No investigation meeting or disciplinary hearing took place and she was not offered an appeal."
Law relied on (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s98 (sha256 98cf854c5298)
      "the reason (or, if more than one, the principal reason) for the dismissal"
      "either a reason falling within subsection (2) or some other substantial reason of a kind such as to justify the dismissal of an employee holding the position which the employee held"

## 5. Has the employee suffered financial loss attributable to the dismissal that is recoverable as a compensatory award?
**Answer: NO** [grounded]
Reasoning (on-device model): The employee's claim for a compensatory award is subject to the statutory cap of 52 weeks' pay, which in this case is £48,500 a year divided by 52 weeks, resulting in a cap of approximately £932 per week. The employee's gross pay is £932 per week, so the maximum compensatory award is capped at 52 weeks' pay, which is the same as her weekly pay. Therefore, the award cannot exceed this amount, and there is no evidence that the employee suffered additional financial loss attributable to the dismissal that is recoverable as a compensatory award.
Client facts relied on (verbatim from the account):
  > "She has been unable to find new work."
  > "Her gross pay was £48,500 a year (about £932 a week)."
Law relied on (statute fetched by PIR, sha256-verified on device):
  - uk/ukpga/1996/18/s124 (sha256 7d7be23f7c54)
      "shall not exceed the amount specified in subsection (1ZA)"
      "Subsection (1) shall not apply to compensation awarded, or a compensatory award made, to a person in a case where he is regarded as unfairly dismissed by virtue of section 100, 103A, 105(3) or 105(6A)"
If not met: The employee will not be entitled to a compensatory award under section 123, or any compensatory award will be reduced to zero.
