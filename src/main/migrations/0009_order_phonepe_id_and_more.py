# Generated by Django 4.2.15 on 2024-09-11 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0008_alter_legalcontent_content"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="phonepe_id",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="PhonePe Payment Id"
            ),
        ),
        migrations.AddField(
            model_name="order",
            name="phonepe_merchant_transaction_id",
            field=models.CharField(
                blank=True,
                max_length=36,
                null=True,
                verbose_name="PhonePe Transaction Id",
            ),
        ),
    ]