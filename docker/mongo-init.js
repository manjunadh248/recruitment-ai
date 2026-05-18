// ═══════════════════════════════════════════════════════════
// RecruitAI — MongoDB Initialization Script
// Creates the database, user, and initial collections
// ═══════════════════════════════════════════════════════════

db = db.getSiblingDB('recruitai');

// Create application user
db.createUser({
    user: 'recruitai_user',
    pwd: 'recruitai_pass',
    roles: [
        { role: 'readWrite', db: 'recruitai' }
    ]
});

// ─── MVP Collections ─────────────────────────────────────

// Users
db.createCollection('users');
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "created_at": -1 });

// Resumes
db.createCollection('resumes');
db.resumes.createIndex({ "user_id": 1, "created_at": -1 });
db.resumes.createIndex({ "user_id": 1, "is_primary": 1 });

// Jobs
db.createCollection('jobs');
db.jobs.createIndex({ "title": "text", "company": "text", "description": "text" });
db.jobs.createIndex({ "source": 1, "status": 1 });
db.jobs.createIndex({ "created_at": -1 });

// ATS Scores
db.createCollection('ats_scores');
db.ats_scores.createIndex({ "resume_id": 1, "job_id": 1 }, { unique: true });
db.ats_scores.createIndex({ "user_id": 1, "overall_score": -1 });

// Optimized Resumes
db.createCollection('optimized_resumes');
db.optimized_resumes.createIndex({ "user_id": 1, "job_id": 1 });
db.optimized_resumes.createIndex({ "user_id": 1, "created_at": -1 });

// Job Matches
db.createCollection('job_matches');
db.job_matches.createIndex({ "user_id": 1, "match_score": -1 });
db.job_matches.createIndex({ "user_id": 1, "job_id": 1 }, { unique: true });

// Skill Profiles
db.createCollection('skill_profiles');
db.skill_profiles.createIndex({ "user_id": 1 }, { unique: true });

print('✅ RecruitAI database initialized with MVP collections and indexes');
