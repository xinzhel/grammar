# A Fictitious Company Environment

## Generating Company Profile
### Prompt for GPT-4: Your job is to make up information in a fictitious company called "Aurp" that provides structural engineering consultancy services. All the information should be NOT REAL.
company_profile = """     
Company Profile
**Name**: Aurp Structural Engineering Consultants
**Founded**: 1995
**Headquarters**: Technopolis, New Atlantis
**CEO**: Dr. Helena Quantum
**Employees**: 250

Services Offered
**Bespoke Architectural Solutions**: Collaborating with architects to design unique, aesthetically pleasing, and functional buildings.
**Sustainable Urban Planning**: Integrating eco-friendly materials and green technologies to reduce environmental impact.
**Structural Health Monitoring**: Deploying sensors and systems for real-time assessment of structural integrity."""


## Generating organizational structure
#### Prompt for GPT-4: Given {company_profile}, generate a project-oriented organizational structure similar to Aurecon or  Arup, including people names and job titles 
job_to_employees = {
    'Chief Executive Officer (CEO)': ['Dr. Helena Quantum'],
    'Chief Operating Officer (COO)': ['Marcus Aurelius'],
    'Chief Technical Officer (CTO)': ['Nikola Tesla'],
    'Director of Engineering': ['Ada Lovelace'],
    'Director of Sustainability': ['Rachel Carson'],
    'Project Director': ['Leonardo Da Vinci', 'Marie Curie'],
    'Project Manager': ['Alan Turing', 'Grace Hopper', 'Hedy Lamarr', 'George Washington Carver'],
    'Assistant Project Manager': ['Isaac Newton', 'Galileo Galilei'],
    'Project Coordinator': ['Rosalind Franklin', 'Mae Jemison', 'Chien-Shiung Wu'],
    'Lead Structural Engineer': ['Gustave Eiffel'],
    'Architectural Liaison Engineer': ['Frank Lloyd Wright'],
    'Sustainability Consultant': ['John Muir', 'Greta Thunberg'],
    'Structural Health Monitoring Engineer': ['Alexander Graham Bell'],
    'Design Engineer': ['Steve Jobs', 'Leonardo da Vinci'],
    'BIM (Building Information Modeling) Manager': ['Henrietta Leavitt'],
    'Finance Manager': ['Warren Buffett'],
    'Human Resources Manager': ['Sheryl Sandberg'],
    'Marketing and Communications Manager': ['Don Draper'],
    'IT Support Specialist': ['Linus Torvalds', 'Ada Lovelace']
}


## Generating Employee Information (Job Titles, Employee Names and Supervisor)
### Prompt for GPT-4: Given the above context ({company_profile} and {job_to_employees}), please make up job title, department and Direct Supervisor/Manager for all the employees above
employees = {
    "Dr. Helena Quantum": ["Chief Executive Officer (CEO)", "Executive Management", "Direct Supervisor/Manager: Board of Directors"],
    "Marcus Aurelius": ["Chief Operating Officer (COO)", "Operations", "Direct Supervisor/Manager: Dr. Helena Quantum"],
    "Nikola Tesla": ["Chief Technical Officer (CTO)", "Technology and Innovation", "Direct Supervisor/Manager: Dr. Helena Quantum"],
    "Ada Lovelace": ["Director of Engineering", "Engineering", "Direct Supervisor/Manager: Nikola Tesla"],
    "Rachel Carson": ["Director of Sustainability", "Sustainability Initiatives", "Direct Supervisor/Manager: Marcus Aurelius"],
    "Leonardo Da Vinci": ["Project Director", "Special Projects", "Direct Supervisor/Manager: Ada Lovelace"],
    "Marie Curie": ["Project Director", "Research and Development Projects", "Direct Supervisor/Manager: Ada Lovelace"],
    "Alan Turing": ["Project Manager", "Technology Integration Projects", "Direct Supervisor/Manager: Leonardo Da Vinci"],
    "Grace Hopper": ["Project Manager", "Software Development for Engineering Tools", "Direct Supervisor/Manager: Leonardo Da Vinci"],
    "Hedy Lamarr": ["Project Manager", "Communication Systems Projects", "Direct Supervisor/Manager: Marie Curie"],
    "George Washington Carver": ["Project Manager", "Sustainable Materials Research", "Direct Supervisor/Manager: Marie Curie"],
    "Isaac Newton": ["Assistant Project Manager", "Physics Applications in Structural Design", "Direct Supervisor/Manager: Alan Turing"],
    "Galileo Galilei": ["Assistant Project Manager", "Observational Technologies for Construction", "Direct Supervisor/Manager: Grace Hopper"],
    "Rosalind Franklin": ["Project Coordinator", "Engineering Documentation and Compliance", "Direct Supervisor/Manager: Hedy Lamarr"],
    "Mae Jemison": ["Project Coordinator", "Space Utilization and Design", "Direct Supervisor/Manager: George Washington Carver"],
    "Chien-Shiung Wu": ["Project Coordinator", "Quantum Mechanics in Structural Engineering", "Direct Supervisor/Manager: Isaac Newton"],
    "Gustave Eiffel": ["Lead Structural Engineer", "Structural Engineering", "Direct Supervisor/Manager: Ada Lovelace"],
    "Frank Lloyd Wright": ["Architectural Liaison Engineer", "Architectural Integration", "Direct Supervisor/Manager: Ada Lovelace"],
    "John Muir": ["Sustainability Consultant", "Environmental Impact Analysis", "Direct Supervisor/Manager: Rachel Carson"],
    "Greta Thunberg": ["Sustainability Consultant", "Climate Change Adaptation Strategies", "Direct Supervisor/Manager: Rachel Carson"],
    "Alexander Graham Bell": ["Structural Health Monitoring Engineer", "Structural Integrity Assessment", "Direct Supervisor/Manager: Nikola Tesla"],
    "Steve Jobs": ["Design Engineer", "User Interface Design for Engineering Software", "Direct Supervisor/Manager: Nikola Tesla"],
    "Leonardo Vinci": ["Design Engineer", "Conceptual Design and Visualization", "Direct Supervisor/Manager: Nikola Tesla"],
    "Henrietta Leavitt": ["BIM (Building Information Modeling) Manager", "Digital Construction Management", "Direct Supervisor/Manager: Ada Lovelace"],
    "Warren Buffett": ["Finance Manager", "Finance", "Direct Supervisor/Manager: Marcus Aurelius"],
    "Sheryl Sandberg": ["Human Resources Manager", "Human Resources", "Direct Supervisor/Manager: Marcus Aurelius"],
    "Don Draper": ["Marketing and Communications Manager", "Marketing and Public Relations", "Direct Supervisor/Manager: Marcus Aurelius"],
    "Linus Torvalds": ["IT Support Specialist", "Information Technology", "Direct Supervisor/Manager: Nikola Tesla"],
    "Ada Lovelace (IT)": ["IT Support Specialist", "Information Technology", "Direct Supervisor/Manager: Nikola Tesla"]
}



## Generating Client Information
### Prompt for GPT-4: Given the above context,  akeup 10 clients the company serves/served in different industries
clients = {
    "Quantum Communications Corp": {
        "Industry": "Technology and Communications Infrastructure",
        "Location": "Silicon Valley, USA"
    },
    "Skyline Developers": {
        "Industry": "Real Estate",
        "Location": "Dubai, UAE"
    },
    "Blue Horizon Hotels": {
        "Industry": "Hospitality",
        "Location": "Maldives"
    },
    "Greenworld Resorts": {
        "Industry": "Hospitality",
        "Location": "Costa Rica"
    },
    "Pinnacle Health Group": {
        "Industry": "Healthcare and Hospital",
        "Location": "London, UK"
    },
    "Future Tech Innovations": {
        "Industry": "Technology and Communications Infrastructure",
        "Location": "Tokyo, Japan"
    },
    "Urban Oasis Developments": {
        "Industry": "Real Estate",
        "Location": "New York City, USA"
    },
    "Serene Stays Hospitality": {
        "Industry": "Hospitality",
        "Location": "Paris, France"
    },
    "Vista Healthcare Solutions": {
        "Industry": "Healthcare and Hospital",
        "Location": "Mumbai, India"
    },
    "EcoSpace Real Estate": {
        "Industry": "Real Estate",
        "Location": "Sydney, Australia"
    }
}

## Project
### Prompt for GPT-4: Given the above context, make up projects including name, location, start date, end date, client, project director, project manager.
projects = [
    {
        "Name": "Quantum Data Center Expansion",
        "Location": "Palo Alto, USA",
        "Start Date": "2023-01-15",
        "End Date": "2024-06-30",
        "Client": "Quantum Communications Corp",
        "Project Director": "Leonardo Da Vinci",
        "Project Manager": "Alan Turing"
    },
    {
        "Name": "Dubai Skyline Tower",
        "Location": "Dubai, UAE",
        "Start Date": "2022-09-01",
        "End Date": "2025-12-31",
        "Client": "Skyline Developers",
        "Project Director": "Marie Curie",
        "Project Manager": "Grace Hopper"
    },
    {
        "Name": "Blue Lagoon Luxury Resort",
        "Location": "Baa Atoll, Maldives",
        "Start Date": "2023-04-01",
        "End Date": "2025-05-20",
        "Client": "Blue Horizon Hotels",
        "Project Director": "Leonardo Da Vinci",
        "Project Manager": "Hedy Lamarr"
    },
    {
        "Name": "Eco Retreat Development",
        "Location": "Guanacaste, Costa Rica",
        "Start Date": "2022-11-15",
        "End Date": "2024-08-30",
        "Client": "Greenworld Resorts",
        "Project Director": "Marie Curie",
        "Project Manager": "George Washington Carver"
    },
    {
        "Name": "Central City Medical Hub",
        "Location": "London, UK",
        "Start Date": "2021-07-01",
        "End Date": "2023-09-30",
        "Client": "Pinnacle Health Group",
        "Project Director": "Leonardo Da Vinci",
        "Project Manager": "Alan Turing"
    },
    {
        "Name": "Innovative Tech Park",
        "Location": "Shibuya, Tokyo, Japan",
        "Start Date": "2023-02-01",
        "End Date": "2025-03-15",
        "Client": "Future Tech Innovations",
        "Project Director": "Marie Curie",
        "Project Manager": "Grace Hopper"
    },
    {
        "Name": "Metropolitan Luxury Apartments",
        "Location": "Manhattan, New York City, USA",
        "Start Date": "2022-05-01",
        "End Date": "2024-12-31",
        "Client": "Urban Oasis Developments",
        "Project Director": "Leonardo Da Vinci",
        "Project Manager": "Hedy Lamarr"
    },
    {
        "Name": "Champs-Élysées Boutique Hotel",
        "Location": "Paris, France",
        "Start Date": "2023-03-01",
        "End Date": "2024-10-30",
        "Client": "Serene Stays Hospitality",
        "Project Director": "Marie Curie",
        "Project Manager": "George Washington Carver"
    },
    {
        "Name": "Advanced Health Research Facility",
        "Location": "Mumbai, India",
        "Start Date": "2023-01-10",
        "End Date": "2024-07-25",
        "Client": "Vista Healthcare Solutions",
        "Project Director": "Leonardo Da Vinci",
        "Project Manager": "Alan Turing"
    },
    {
        "Name": "Harbour View Green Spaces",
        "Location": "Sydney, Australia",
        "Start Date": "2022-08-01",
        "End Date": "2025-02-20",
        "Client": "EcoSpace Real Estate",
        "Project Director": "Marie Curie",
        "Project Manager": "Grace Hopper"
    }
]
### assert project.client in clients
for project in projects:
    assert project["Client"] in clients
### assert project.project_director in employees
for project in projects:
    assert project["Project Director"] in employees
### assert project.project_manager in employees
for project in projects:
    assert project["Project Manager"] in employees
    

## Generating Project Reports
### Prompts for GPT4: Make up a project report spreading the following basic information across the project but not assembling them together:

