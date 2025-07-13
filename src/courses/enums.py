from enum import StrEnum


class CourseLevelEnum(StrEnum):
    """Enum class representing course levels in the system."""

    BASIC = 'basic'  # For user just starting learning
    MEDIUM = 'medium'  # For user with intermediate knowledge
    PROFESSIONAL = 'professional'  # For user with advanced knowledge


class CurrencyEnum(StrEnum):
    """Enum class representing currencies in the system."""

    USD = 'usd'  # USD
    EUR = 'eur'  # Euro


class AvailableLanguagesEnum(StrEnum):
    """Enum class representing available languages for course."""

    EN = 'en'  # English
    DE = 'de'  # Deutsch
    FR = 'fr'  # French

class Professions(StrEnum):
    """Enum class representing professions for author."""
    SOFTWARE_ENGINEER = "Software Engineer"
    BACKEND_DEVELOPER = "Backend Developer"
    FRONTEND_DEVELOPER = "Frontend Developer"
    FULLSTACK_DEVELOPER = "Fullstack Developer"
    MOBILE_DEVELOPER = "Mobile App Developer"
    GAME_DEVELOPER = "Game Developer"
    DEVOPS_ENGINEER = "DevOps Engineer"
    SYSTEM_ADMINISTRATOR = "System Administrator"
    NETWORK_ENGINEER = "Network Engineer"
    SECURITY_ENGINEER = "Cybersecurity Engineer"
    QA_ENGINEER = "QA Engineer"
    AUTOMATION_ENGINEER = "Automation Engineer"
    DATA_SCIENTIST = "Data Scientist"
    MACHINE_LEARNING_ENGINEER = "Machine Learning Engineer"
    AI_ENGINEER = "AI Engineer"
    DATA_ENGINEER = "Data Engineer"
    DATABASE_ADMINISTRATOR = "Database Administrator"
    CLOUD_ENGINEER = "Cloud Engineer"
    ROBOTICS_ENGINEER = "Robotics Engineer"
    PRODUCT_MANAGER = "Product Manager"
    PROJECT_MANAGER = "Project Manager"
    SCRUM_MASTER = "Scrum Master"
    BUSINESS_ANALYST = "Business Analyst"
    TECHNICAL_WRITER = "Technical Writer"
    UX_UI_DESIGNER = "UX/UI Designer"
    GRAPHIC_DESIGNER = "Graphic Designer"
    MOTION_DESIGNER = "Motion Designer"
    VIDEO_EDITOR = "Video Editor"
    CONTENT_WRITER = "Content Writer"
    COPYWRITER = "Copywriter"
    MARKETING_SPECIALIST = "Marketing Specialist"
    DIGITAL_MARKETER = "Digital Marketer"
    SEO_SPECIALIST = "SEO Specialist"
    SMM_SPECIALIST = "Social Media Specialist"
    TECH_LEAD = "Tech Lead"
    SOFTWARE_ARCHITECT = "Software Architect"
    CLOUD_ARCHITECT = "Cloud Architect"
    SOLUTIONS_ARCHITECT = "Solutions Architect"
    CYBERSECURITY_ANALYST = "Cybersecurity Analyst"
    PENETRATION_TESTER = "Penetration Tester"
    UI_DEVELOPER = "UI Developer"
    WEB_DEVELOPER = "Web Developer"
    SITE_RELIABILITY_ENGINEER = "Site Reliability Engineer"
    MLOPS_ENGINEER = "MLOps Engineer"
    ANALYTICS_ENGINEER = "Analytics Engineer"
    DATA_ANALYST = "Data Analyst"
    ETL_DEVELOPER = "ETL Developer"
    RESEARCH_SCIENTIST = "Research Scientist (AI/ML)"
    GAME_DESIGNER = "Game Designer"
    COMPUTER_VISION_ENGINEER = "Computer Vision Engineer"
    NLP_ENGINEER = "NLP Engineer"
    HARDWARE_ENGINEER = "Hardware Engineer"
    EMBEDDED_ENGINEER = "Embedded Systems Engineer"
    FPGA_ENGINEER = "FPGA Engineer"
    TECH_RECRUITER = "Tech Recruiter"
    IT_TRAINER = "IT Trainer"
    INSTRUCTOR = "Tech Instructor"