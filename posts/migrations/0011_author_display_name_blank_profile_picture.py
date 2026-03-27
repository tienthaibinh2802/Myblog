from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0010_comment"),
    ]

    operations = [
        migrations.AddField(
            model_name="author",
            name="display_name",
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AlterField(
            model_name="author",
            name="profile_picture",
            field=models.ImageField(blank=True, upload_to=""),
        ),
    ]
