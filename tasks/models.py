

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class TaskList(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom de la liste")
    description = models.TextField(blank=True, verbose_name="Description")
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_lists",
        verbose_name="Propriétaire"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # Inscrit automatiquement le propriétaire parmi les membres
        if is_new:
            Membership.objects.get_or_create(task_list=self, user=self.owner)


class Membership(models.Model):
    task_list = models.ForeignKey(
        TaskList,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="list_memberships"
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['task_list', 'user'],
                name='unique_tasklist_user_membership'
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.task_list.name}"


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'TODO', 'À faire'
        IN_PROGRESS = 'IN_PROGRESS', 'En cours'
        DONE = 'DONE', 'Terminée'

    task_list = models.ForeignKey(
        TaskList,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    title = models.CharField(max_length=255, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
        verbose_name="Statut"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks"
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        verbose_name="Responsable"
    )
    due_at = models.DateTimeField(null=True, blank=True, verbose_name="Échéance")
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.status == self.Status.DONE and self.completed_at is None:
            self.completed_at = timezone.now()
        elif self.status != self.Status.DONE and self.completed_at is not None:
            self.completed_at = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Comment(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="task_comments"
    )
    body = models.TextField(verbose_name="Commentaire")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Commentaire de {self.author.username}"
