from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Enrollment, Submission, Choice

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    # Lấy enrollment (giả sử user đang login)
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    
    if request.method == 'POST':
        submission = Submission.objects.create(enrollment=enrollment)
        for question in course.question_set.all():
            choice_id = request.POST.get(f'choice_{question.id}')
            if choice_id:
                choice = Choice.objects.get(id=choice_id)
                submission.choices.add(choice)
        submission.save()
        return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    total_score = 0
    possible_score = 0
    
    selected_ids = submission.choices.values_list('id', flat=True)
    
    for question in course.question_set.all():
        possible_score += question.grade
        if question.is_get_score(selected_ids):
            total_score += question.grade
            
    grade_percentage = (total_score / possible_score) * 100 if possible_score > 0 else 0
    passed = grade_percentage >= 80

    context = {
        'course': course,
        'total_score': total_score,
        'possible_score': possible_score,
        'grade_percentage': grade_percentage,
        'passed': passed
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
