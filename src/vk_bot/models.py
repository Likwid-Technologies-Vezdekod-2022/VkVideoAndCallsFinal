from django.db import models


class VkUser(models.Model):
    chat_id = models.CharField(max_length=15, verbose_name='chat_id')
    name = models.CharField(max_length=150, verbose_name='Имя', blank=True)

    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Пользователь Вконтакте'
        verbose_name_plural = 'Пользователи Вконтакте'
        ordering = ['-update_date']

    def __str__(self):
        return f'{self.chat_id} ({self.name})'


class Operator(models.Model):
    number = models.PositiveIntegerField(unique=True)
    user = models.OneToOneField('VkUser', null=True, blank=True,
                                on_delete=models.SET_NULL)

    url = models.TextField(blank=True)

    free = models.BooleanField(default=True)

    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Оператор'
        verbose_name_plural = 'Операторы'
        ordering = ['-update_date']

    def __str__(self):
        return f'{self.id}'
