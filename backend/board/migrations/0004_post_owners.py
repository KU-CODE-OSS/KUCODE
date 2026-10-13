from django.db import migrations, models


def backfill_post_owners(apps, schema_editor):
    Post = apps.get_model('board', 'Post')
    Member = apps.get_model('login', 'Member')

    members_by_id = {
        str(member_id): member_id
        for member_id in Member.objects.values_list('id', flat=True)
    }
    for post in Post.objects.iterator():
        member_id = members_by_id.get(str(post.author))
        if member_id is not None:
            post.owners.add(member_id)


def no_op_reverse(apps, schema_editor):
    # Removing the field drops this relation automatically on reverse migration.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_alter_member_id'),
        ('board', '0003_alter_post_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='owners',
            field=models.ManyToManyField(
                blank=True,
                help_text="Members who can manage this post and receive response notifications.",
                related_name='owned_posts',
                to='login.member',
            ),
        ),
        migrations.RunPython(backfill_post_owners, no_op_reverse),
    ]
