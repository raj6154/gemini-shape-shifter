# . job_candidate_ranking.py

experience_years = int(input("Enter years of experience: "))
skills_score = int(input("Enter skills score (0-100): "))

education_level = input(
    "Enter education level (diploma/graduate/postgraduate/phd): "
).lower()

interview_score = int(input("Enter interview score (0-100): "))

final_score = 0
experience_bonus = 1.5 * experience_years
skills_bonus = skills_score * 0.5
interview_bonus = interview_score * 0.3


if skills_score < 40 or interview_score < 30:
    print("Candidate rejected hehehehehehehe.")
else:

    if experience_years < 1:
        print("fresher candidate.")
    elif experience_years >= 1 and experience_years < 3:
        print("junior level candidate.")
    elif experience_years >= 3 and experience_years < 7:
        print("mid level candidate.")
    elif experience_years >= 7:
        print("senior level candidate.")

    if education_level == "diploma":
        education_bonus = 2
    elif education_level == "graduate":
        education_bonus = 5
    elif education_level == "postgraduate":
        education_bonus = 8
    elif education_level == "phd":
        education_bonus = 12

    final_score = skills_score + interview_score + experience_bonus + education_bonus
    print("Final candidate score is:", final_score)

    if final_score >= 85:
        print("excellent.")
    elif final_score >= 70:
        print("good.")
    elif final_score >= 60:
        print("average.")
    else:
        print("poor.")
