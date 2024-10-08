# Generated by Django 4.2.9 on 2024-07-28 23:40

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE VIEW assignment_result_view AS
                SELECT 
                    a.id AS assignment_id,
                    a.title,
                    a.description,
                    a.due_date,
                    ar.id AS assignment_result_id,
                    ar.user_id,
                    ar.submission_date,
                    ar.file,
                    ar.grade,
                    a.id || '-' || ar.id AS id
                FROM home_assignment AS a
                LEFT JOIN home_assignmentresult AS ar ON a.id = ar.assignment_id
                WHERE ar.id IS NOT NULL  -- Exclude rows where assignment_result_id is NULL
                UNION ALL
                SELECT 
                    a.id AS assignment_id,
                    a.title,
                    a.description,
                    a.due_date,
                    -1 AS assignment_result_id,
                    -1 AS user_id,
                    '1970-01-01 00:00:00' AS submission_date,
                    '' AS file,
                    0.0 AS grade,
                    a.id || '-0' AS id
                FROM home_assignment AS a;
                """,
            reverse_sql="DROP VIEW IF EXISTS assignment_result_view;",
        ),
    ]
