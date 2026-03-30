from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0011_author_display_name_blank_profile_picture"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="status",
            field=models.CharField(
                choices=[("draft", "Draft"), ("published", "Published")],
                default="published",
                max_length=20,
            ),
        ),
    ]
