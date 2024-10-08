# Generated by Django 4.2.15 on 2024-09-12 06:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_phonepepaymentrequestdetail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='pdf_file',
            field=models.FileField(max_length=500, upload_to='pdfs/'),
        ),
        migrations.AlterField(
            model_name='item',
            name='price',
            field=models.DecimalField(decimal_places=2, default=1.0, max_digits=10),
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(max_length=500, upload_to='item_images/')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='main.item')),
            ],
        ),
    ]
