"""Add feedback table and dual report columns

Revision ID: 693c901b2616
Revises: 2ec613c9177f
Create Date: 2025-10-03 21:08:25.395400

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '693c901b2616'
down_revision = '2ec613c9177f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create feedback_submissions table
    op.create_table('feedback_submissions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('intake_sessions.id'), nullable=False),
        sa.Column('conversation_rating', sa.Integer(), nullable=False),
        sa.Column('patient_report_rating', sa.Integer(), nullable=False),
        sa.Column('clinician_report_rating', sa.Integer(), nullable=False),
        sa.Column('would_use', sa.String(50), nullable=False),
        sa.Column('strength', sa.Text(), nullable=True),
        sa.Column('concern', sa.Text(), nullable=True),
        sa.Column('missing_patient', sa.Text(), nullable=True),
        sa.Column('missing_clinician', sa.Text(), nullable=True),
        sa.Column('additional_comments', sa.Text(), nullable=True),
        sa.Column('tester_email', sa.String(255), nullable=True),
        sa.Column('tester_name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=True)
    )
    
    # Add columns to intake_reports table
    op.add_column('intake_reports', sa.Column('clinician_report_data', sa.JSON(), nullable=True))
    op.add_column('intake_reports', sa.Column('patient_pdf_path', sa.String(500), nullable=True))
    op.add_column('intake_reports', sa.Column('clinician_pdf_path', sa.String(500), nullable=True))
    op.add_column('intake_reports', sa.Column('feedback_submitted', sa.Boolean(), nullable=True))


def downgrade() -> None:
    # Remove columns from intake_reports table
    op.drop_column('intake_reports', 'feedback_submitted')
    op.drop_column('intake_reports', 'clinician_pdf_path')
    op.drop_column('intake_reports', 'patient_pdf_path')
    op.drop_column('intake_reports', 'clinician_report_data')
    
    # Drop feedback_submissions table
    op.drop_table('feedback_submissions')

