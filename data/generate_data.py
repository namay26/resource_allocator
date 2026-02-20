import json
import random
from datetime import datetime, timedelta, time

random.seed(42)

START_DATE = datetime(2025, 7, 1)
END_DATE = datetime(2025, 9, 30)
NUM_DAYS = (END_DATE - START_DATE).days + 1


# HARD CODED THIS because DATA FROM THE LLMs WAS NOT GOOD ENOUGH
ACTIVITIES = [
    # Priority 1-10: Critical medications
    {"id": 1,  "name": "Morning blood pressure medication", "type": "Medication consumption", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "07:00", "facilitator": None, "location": "Any", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": "Take with water on empty stomach", "backup_activities": ["Evening blood pressure medication shift"], "skip_adjustments": "Take as soon as remembered, skip if close to next dose", "metrics": ["blood_pressure", "adherence"], "details": "Take 10mg Lisinopril"},
    {"id": 2,  "name": "Thyroid medication", "type": "Medication consumption", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "06:30", "facilitator": None, "location": "Any", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": "Take 30min before breakfast on empty stomach", "backup_activities": [], "skip_adjustments": "Take next day, do not double dose", "metrics": ["TSH_levels", "adherence"], "details": "Take 50mcg Levothyroxine"},
    {"id": 3,  "name": "Evening statin medication", "type": "Medication consumption", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "21:00", "facilitator": None, "location": "Any", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": [], "skip_adjustments": "Take as soon as remembered", "metrics": ["cholesterol", "adherence"], "details": "Take 20mg Atorvastatin"},
    {"id": 4,  "name": "Vitamin D supplement", "type": "Medication consumption", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "08:00", "facilitator": None, "location": "Any", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": "Take with fatty meal for absorption", "backup_activities": [], "skip_adjustments": "Skip and resume next day", "metrics": ["vitamin_d_levels", "adherence"], "details": "Take 2000 IU Vitamin D3"},
    {"id": 5,  "name": "Omega-3 supplement", "type": "Medication consumption", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "08:00", "facilitator": None, "location": "Any", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": "Take with meal", "backup_activities": [], "skip_adjustments": "Skip and resume next day", "metrics": ["triglycerides", "adherence"], "details": "Take 1000mg Fish Oil"},
    {"id": 6,  "name": "Magnesium supplement", "type": "Medication consumption", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "21:30", "facilitator": None, "location": "Any", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": [], "skip_adjustments": "Skip and resume next day", "metrics": ["sleep_quality", "adherence"], "details": "Take 400mg Magnesium Glycinate"},
    {"id": 7,  "name": "Probiotic supplement", "type": "Medication consumption", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "07:30", "facilitator": None, "location": "Any", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": "Take on empty stomach", "backup_activities": [], "skip_adjustments": "Skip and resume next day", "metrics": ["gut_health", "adherence"], "details": "Take 1 capsule probiotic blend"},

    # Priority 8-20: Critical fitness
    {"id": 8,  "name": "Morning walk", "type": "Fitness routine", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 30, "preferred_time": "06:45", "facilitator": None, "location": "Outdoors / Gym", "remote_possible": False, "equipment": ["heart_rate_monitor"], "specialist": None, "allied_health": None, "prep": "Light stretching", "backup_activities": ["Indoor treadmill walk"], "skip_adjustments": "Add 10 min to afternoon activity", "metrics": ["steps", "heart_rate", "duration"], "details": "Brisk walk, maintain HR between 100-120"},
    {"id": 9,  "name": "Zone 2 cardio - cycling", "type": "Fitness routine", "frequency": "weekly", "times_per_period": 3, "period": "week", "duration_min": 45, "preferred_time": "09:00", "facilitator": "trainer_mike", "location": "Gym", "remote_possible": False, "equipment": ["stationary_bike", "heart_rate_monitor"], "specialist": None, "allied_health": None, "prep": "Warm up 5 min", "backup_activities": ["Zone 2 cardio - rowing", "Zone 2 cardio - elliptical"], "skip_adjustments": "Replace with extra walking session", "metrics": ["heart_rate", "duration", "distance", "calories"], "details": "Maintain HR between 120-140 bpm"},
    {"id": 10, "name": "Strength training - upper body", "type": "Fitness routine", "frequency": "weekly", "times_per_period": 2, "period": "week", "duration_min": 60, "preferred_time": "10:00", "facilitator": "trainer_mike", "location": "Gym", "remote_possible": False, "equipment": ["dumbbells", "bench_press", "cable_machine"], "specialist": None, "allied_health": None, "prep": "Dynamic warm-up 10 min", "backup_activities": ["Bodyweight upper body workout"], "skip_adjustments": "Shift to next available day within same week", "metrics": ["weight_lifted", "reps", "sets", "RPE"], "details": "Focus on compound movements: bench press, rows, overhead press"},
    {"id": 11, "name": "Strength training - lower body", "type": "Fitness routine", "frequency": "weekly", "times_per_period": 2, "period": "week", "duration_min": 60, "preferred_time": "10:00", "facilitator": "trainer_mike", "location": "Gym", "remote_possible": False, "equipment": ["squat_rack", "leg_press", "dumbbells"], "specialist": None, "allied_health": None, "prep": "Dynamic warm-up 10 min, foam rolling", "backup_activities": ["Bodyweight lower body workout"], "skip_adjustments": "Shift to next available day within same week", "metrics": ["weight_lifted", "reps", "sets", "RPE"], "details": "Focus on squats, deadlifts, lunges"},
    {"id": 12, "name": "Core stability workout", "type": "Fitness routine", "frequency": "weekly", "times_per_period": 3, "period": "week", "duration_min": 20, "preferred_time": "10:30", "facilitator": None, "location": "Gym / Home", "remote_possible": True, "equipment": ["yoga_mat", "stability_ball"], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Plank routine at home"], "skip_adjustments": "Add to next session", "metrics": ["duration", "plank_time"], "details": "Planks, dead bugs, bird dogs, pallof press"},
    {"id": 13, "name": "Flexibility & mobility routine", "type": "Fitness routine", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 15, "preferred_time": "21:00", "facilitator": None, "location": "Home", "remote_possible": True, "equipment": ["yoga_mat", "foam_roller"], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["5-minute stretch sequence"], "skip_adjustments": "Do abbreviated version next day", "metrics": ["flexibility_score", "adherence"], "details": "Full body stretching focusing on hip flexors, hamstrings, shoulders"},
    {"id": 14, "name": "Balance & proprioception training", "type": "Fitness routine", "frequency": "weekly", "times_per_period": 2, "period": "week", "duration_min": 15, "preferred_time": "09:30", "facilitator": None, "location": "Gym / Home", "remote_possible": True, "equipment": ["balance_board", "yoga_mat"], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Single-leg stance practice"], "skip_adjustments": "Add to next flexibility session", "metrics": ["balance_time", "adherence"], "details": "Single-leg stands, BOSU ball work, tandem walking"},
    {"id": 15, "name": "HIIT session", "type": "Fitness routine", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 30, "preferred_time": "09:00", "facilitator": "trainer_mike", "location": "Gym", "remote_possible": False, "equipment": ["rowing_machine", "kettlebells", "heart_rate_monitor"], "specialist": None, "allied_health": None, "prep": "Thorough warm-up 10 min", "backup_activities": ["Tabata bodyweight workout"], "skip_adjustments": "Do not add extra HIIT, replace with Zone 2", "metrics": ["heart_rate_max", "heart_rate_recovery", "calories"], "details": "4x4 min intervals at 85-95% max HR, 3 min recovery"},
    {"id": 16, "name": "Swimming", "type": "Fitness routine", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 45, "preferred_time": "07:00", "facilitator": None, "location": "Pool", "remote_possible": False, "equipment": ["swim_goggles"], "specialist": None, "allied_health": None, "prep": "Light shoulder warm-up", "backup_activities": ["Aqua jogging", "Zone 2 cardio - cycling"], "skip_adjustments": "Replace with cycling or rowing", "metrics": ["laps", "duration", "heart_rate"], "details": "Mixed strokes, focus on technique and endurance"},
    {"id": 17, "name": "Eye exercises", "type": "Fitness routine", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 10, "preferred_time": "12:00", "facilitator": None, "location": "Any", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": [], "skip_adjustments": "Do at next break", "metrics": ["adherence", "eye_strain_score"], "details": "20-20-20 rule practice, focus shifting, eye circles"},
    {"id": 18, "name": "Grip strength training", "type": "Fitness routine", "frequency": "weekly", "times_per_period": 3, "period": "week", "duration_min": 10, "preferred_time": "10:45", "facilitator": None, "location": "Gym / Home", "remote_possible": True, "equipment": ["grip_strengthener"], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Towel hang"], "skip_adjustments": "Add to next strength session", "metrics": ["grip_strength_kg", "adherence"], "details": "Farmer carries, dead hangs, gripper sets"},
    {"id": 19, "name": "Yoga session", "type": "Fitness routine", "frequency": "weekly", "times_per_period": 2, "period": "week", "duration_min": 45, "preferred_time": "18:00", "facilitator": "yoga_instructor_sarah", "location": "Studio / Home", "remote_possible": True, "equipment": ["yoga_mat", "yoga_blocks"], "specialist": None, "allied_health": None, "prep": "Empty stomach preferred", "backup_activities": ["Guided yoga video at home"], "skip_adjustments": "Do 15-min home flow", "metrics": ["flexibility_score", "stress_level", "adherence"], "details": "Vinyasa flow focusing on breath and movement coordination"},
    {"id": 20, "name": "Breathing exercises", "type": "Fitness routine", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 10, "preferred_time": "22:00", "facilitator": None, "location": "Home", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": [], "skip_adjustments": "Do abbreviated 3-min version", "metrics": ["HRV", "stress_level", "adherence"], "details": "Box breathing: 4-4-4-4 pattern, 10 rounds"},

    # Priority 21-40: Nutrition / Food
    {"id": 21, "name": "Breakfast - high protein", "type": "Food consumption", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 20, "preferred_time": "07:30", "facilitator": None, "location": "Home / Kitchen", "remote_possible": False, "equipment": ["kitchen"], "specialist": None, "allied_health": None, "prep": "Prep ingredients night before", "backup_activities": ["Protein shake with greens"], "skip_adjustments": "Have protein shake instead", "metrics": ["protein_grams", "calories", "adherence"], "details": "30-40g protein: eggs, Greek yogurt, or protein oats"},
    {"id": 22, "name": "Morning green smoothie", "type": "Food consumption", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 10, "preferred_time": "07:45", "facilitator": None, "location": "Home / Kitchen", "remote_possible": False, "equipment": ["blender"], "specialist": None, "allied_health": None, "prep": "Pre-portion smoothie bags in freezer", "backup_activities": ["Green juice from store"], "skip_adjustments": "Have extra vegetables at lunch", "metrics": ["vegetable_servings", "adherence"], "details": "Spinach, kale, banana, berries, flax seeds, protein powder"},
    {"id": 23, "name": "Mid-morning snack", "type": "Food consumption", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 10, "preferred_time": "10:00", "facilitator": None, "location": "Any", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": "Pre-pack snacks", "backup_activities": ["Handful of almonds"], "skip_adjustments": "Add to lunch portion", "metrics": ["calories", "adherence"], "details": "Mixed nuts, fruit, or protein bar. Keep under 200 cal"},
    {"id": 24, "name": "Lunch - balanced meal", "type": "Food consumption", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 30, "preferred_time": "12:30", "facilitator": None, "location": "Home / Office", "remote_possible": False, "equipment": ["kitchen"], "specialist": None, "allied_health": None, "prep": "Meal prep on Sunday", "backup_activities": ["Healthy takeout option from approved list"], "skip_adjustments": "Ensure dinner covers macros", "metrics": ["protein_grams", "calories", "vegetable_servings", "adherence"], "details": "Lean protein + complex carbs + vegetables. 500-600 cal target"},
    {"id": 25, "name": "Afternoon snack", "type": "Food consumption", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 10, "preferred_time": "15:30", "facilitator": None, "location": "Any", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": "Pre-pack snacks", "backup_activities": ["Apple with almond butter"], "skip_adjustments": "Skip if not hungry", "metrics": ["calories", "adherence"], "details": "Greek yogurt with berries or hummus with veggies"},
    {"id": 26, "name": "Dinner - anti-inflammatory", "type": "Food consumption", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 30, "preferred_time": "18:30", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": ["kitchen"], "specialist": None, "allied_health": None, "prep": "Meal prep on Sunday and Wednesday", "backup_activities": ["Healthy takeout - Mediterranean"], "skip_adjustments": "Have simple protein + salad", "metrics": ["protein_grams", "calories", "omega3_intake", "adherence"], "details": "Wild salmon/chicken + sweet potato + steamed greens + olive oil"},
    {"id": 27, "name": "Hydration tracking", "type": "Food consumption", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "08:00", "facilitator": None, "location": "Any", "remote_possible": True, "equipment": ["water_bottle"], "specialist": None, "allied_health": None, "prep": "Fill water bottle", "backup_activities": [], "skip_adjustments": "Set hourly reminders", "metrics": ["water_oz", "adherence"], "details": "Target 80oz water daily. Log intake at each meal"},
    {"id": 28, "name": "Electrolyte drink - post workout", "type": "Food consumption", "frequency": "weekly", "times_per_period": 5, "period": "week", "duration_min": 5, "preferred_time": "10:30", "facilitator": None, "location": "Any", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Coconut water"], "skip_adjustments": "Increase plain water intake", "metrics": ["sodium_mg", "potassium_mg", "adherence"], "details": "LMNT or similar, post-exercise"},
    {"id": 29, "name": "Meal prep Sunday", "type": "Food consumption", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 120, "preferred_time": "14:00", "facilitator": None, "location": "Home / Kitchen", "remote_possible": False, "equipment": ["kitchen"], "specialist": None, "allied_health": None, "prep": "Grocery shopping Saturday", "backup_activities": ["Order from meal prep service"], "skip_adjustments": "Do abbreviated prep Monday morning", "metrics": ["meals_prepped", "adherence"], "details": "Prep lunches and dinners for Mon-Wed. Batch cook proteins and grains"},
    {"id": 30, "name": "Meal prep Wednesday", "type": "Food consumption", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 90, "preferred_time": "18:00", "facilitator": None, "location": "Home / Kitchen", "remote_possible": False, "equipment": ["kitchen"], "specialist": None, "allied_health": None, "prep": "Quick grocery run", "backup_activities": ["Order from meal prep service"], "skip_adjustments": "Simple meals Thu-Sat", "metrics": ["meals_prepped", "adherence"], "details": "Prep lunches and dinners for Thu-Sun"},
    {"id": 31, "name": "Collagen peptides drink", "type": "Food consumption", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "09:00", "facilitator": None, "location": "Any", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Bone broth"], "skip_adjustments": "Skip and resume next day", "metrics": ["adherence"], "details": "Mix 10g collagen peptides in coffee or water"},
    {"id": 32, "name": "Pre-workout nutrition", "type": "Food consumption", "frequency": "weekly", "times_per_period": 5, "period": "week", "duration_min": 10, "preferred_time": "08:30", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Banana with peanut butter"], "skip_adjustments": "Train fasted if preferred", "metrics": ["calories", "carbs_grams", "adherence"], "details": "Light carb + protein 30-60 min before training"},
    {"id": 33, "name": "Post-workout protein shake", "type": "Food consumption", "frequency": "weekly", "times_per_period": 5, "period": "week", "duration_min": 5, "preferred_time": "11:00", "facilitator": None, "location": "Gym / Home", "remote_possible": False, "equipment": ["shaker_bottle"], "specialist": None, "allied_health": None, "prep": "Pack shaker bottle and powder", "backup_activities": ["Protein-rich whole food meal"], "skip_adjustments": "Ensure next meal is protein-rich", "metrics": ["protein_grams", "adherence"], "details": "30g whey protein + banana within 30 min post-exercise"},
    {"id": 34, "name": "Herbal tea - evening", "type": "Food consumption", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 10, "preferred_time": "20:30", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": [], "skip_adjustments": "Skip", "metrics": ["sleep_quality", "adherence"], "details": "Chamomile or valerian root tea for sleep support"},

    # Priority 35-55: Therapy sessions
    {"id": 35, "name": "Sauna session", "type": "Therapy", "frequency": "weekly", "times_per_period": 3, "period": "week", "duration_min": 20, "preferred_time": "17:00", "facilitator": None, "location": "Gym / Spa", "remote_possible": False, "equipment": ["sauna"], "specialist": None, "allied_health": None, "prep": "Hydrate well before", "backup_activities": ["Hot bath at home"], "skip_adjustments": "Replace with hot shower contrast therapy", "metrics": ["heart_rate", "session_duration", "adherence"], "details": "Dry sauna at 170-190°F for 15-20 min"},
    {"id": 36, "name": "Cold plunge / ice bath", "type": "Therapy", "frequency": "weekly", "times_per_period": 3, "period": "week", "duration_min": 10, "preferred_time": "17:25", "facilitator": None, "location": "Gym / Spa", "remote_possible": False, "equipment": ["cold_plunge"], "specialist": None, "allied_health": None, "prep": "Breathing exercises before entry", "backup_activities": ["Cold shower 2-3 min"], "skip_adjustments": "Do cold shower at home", "metrics": ["water_temp", "duration", "adherence"], "details": "Cold water at 38-45°F for 2-5 min"},
    {"id": 37, "name": "Red light therapy", "type": "Therapy", "frequency": "weekly", "times_per_period": 5, "period": "week", "duration_min": 15, "preferred_time": "07:15", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": ["red_light_panel"], "specialist": None, "allied_health": None, "prep": "Expose target areas", "backup_activities": ["Morning sunlight exposure 15 min"], "skip_adjustments": "Get extra morning sunlight", "metrics": ["adherence", "skin_quality"], "details": "Full body exposure at 6 inches from panel"},
    {"id": 38, "name": "Compression therapy - legs", "type": "Therapy", "frequency": "weekly", "times_per_period": 3, "period": "week", "duration_min": 30, "preferred_time": "20:00", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": ["compression_boots"], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Manual leg elevation 20 min"], "skip_adjustments": "Elevate legs instead", "metrics": ["recovery_score", "adherence"], "details": "NormaTec boots on recovery setting"},
    {"id": 39, "name": "Massage therapy", "type": "Therapy", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 60, "preferred_time": "16:00", "facilitator": None, "location": "Clinic", "remote_possible": False, "equipment": ["massage_table"], "specialist": None, "allied_health": "massage_therapist_jen", "prep": "Hydrate before session", "backup_activities": ["Self-massage with foam roller 20 min"], "skip_adjustments": "Use percussion massager at home", "metrics": ["pain_scale", "ROM", "adherence"], "details": "Deep tissue focus on upper back, shoulders, and legs"},
    {"id": 40, "name": "Acupuncture session", "type": "Therapy", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 45, "preferred_time": "14:00", "facilitator": None, "location": "Clinic", "remote_possible": False, "equipment": ["acupuncture_needles"], "specialist": None, "allied_health": "acupuncturist_lee", "prep": "Eat light meal 1h before", "backup_activities": ["Acupressure self-treatment"], "skip_adjustments": "Schedule double session next week if available", "metrics": ["pain_scale", "stress_level", "adherence"], "details": "Focus on stress reduction and lower back pain relief"},
    {"id": 41, "name": "Meditation - morning", "type": "Therapy", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 15, "preferred_time": "06:15", "facilitator": None, "location": "Home", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["5-min breathing exercise"], "skip_adjustments": "Do 5-min version", "metrics": ["HRV", "stress_level", "adherence"], "details": "Mindfulness meditation using Headspace app"},
    {"id": 42, "name": "Meditation - evening", "type": "Therapy", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 10, "preferred_time": "21:30", "facilitator": None, "location": "Home", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Body scan relaxation"], "skip_adjustments": "Do deep breathing instead", "metrics": ["sleep_onset_time", "adherence"], "details": "Guided sleep meditation or body scan"},
    {"id": 43, "name": "Foam rolling session", "type": "Therapy", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 10, "preferred_time": "21:15", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": ["foam_roller"], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Lacrosse ball trigger point release"], "skip_adjustments": "Do before next workout", "metrics": ["muscle_soreness", "adherence"], "details": "Focus on IT band, quads, upper back, calves"},
    {"id": 44, "name": "Gratitude journaling", "type": "Therapy", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "22:00", "facilitator": None, "location": "Home", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Mental gratitude practice"], "skip_adjustments": "Do next morning", "metrics": ["mood_score", "adherence"], "details": "Write 3 things grateful for and 1 highlight of the day"},
    {"id": 45, "name": "Sleep hygiene routine", "type": "Therapy", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 15, "preferred_time": "22:00", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": ["blue_light_glasses"], "specialist": None, "allied_health": None, "prep": "Dim lights at 9pm", "backup_activities": [], "skip_adjustments": "At minimum: no screens 30 min before bed", "metrics": ["sleep_onset_time", "sleep_quality", "adherence"], "details": "Blue light blocking, dim lights, cool room to 65°F, no screens"},

    # Priority 46-65: Consultations
    {"id": 46, "name": "Cardiologist check-up", "type": "Consultation", "frequency": "monthly", "times_per_period": 1, "period": "month", "duration_min": 45, "preferred_time": "10:00", "facilitator": None, "location": "Clinic", "remote_possible": True, "equipment": [], "specialist": "dr_patel_cardio", "allied_health": None, "prep": "Bring BP log and medication list", "backup_activities": ["Telehealth cardiologist visit"], "skip_adjustments": "Reschedule within 2 weeks", "metrics": ["blood_pressure", "resting_HR", "ECG_results"], "details": "Review BP trends, medication efficacy, cardiac markers"},
    {"id": 47, "name": "Endocrinologist check-up", "type": "Consultation", "frequency": "monthly", "times_per_period": 1, "period": "month", "duration_min": 45, "preferred_time": "11:00", "facilitator": None, "location": "Clinic", "remote_possible": True, "equipment": [], "specialist": "dr_wong_endo", "allied_health": None, "prep": "Fast for blood work, bring thyroid medication log", "backup_activities": ["Telehealth endo visit"], "skip_adjustments": "Reschedule within 2 weeks", "metrics": ["TSH", "T4", "blood_glucose", "HbA1c"], "details": "Thyroid function review, metabolic panel assessment"},
    {"id": 48, "name": "Physiotherapy session", "type": "Consultation", "frequency": "weekly", "times_per_period": 2, "period": "week", "duration_min": 45, "preferred_time": "14:00", "facilitator": None, "location": "Clinic", "remote_possible": True, "equipment": ["therapy_bands", "yoga_mat"], "specialist": None, "allied_health": "physio_anna", "prep": "Wear comfortable clothing", "backup_activities": ["Home exercise program from physio"], "skip_adjustments": "Do prescribed home exercises", "metrics": ["ROM", "pain_scale", "strength_test", "adherence"], "details": "Lower back rehabilitation, shoulder mobility work"},
    {"id": 49, "name": "Nutritionist consultation", "type": "Consultation", "frequency": "monthly", "times_per_period": 2, "period": "month", "duration_min": 30, "preferred_time": "11:00", "facilitator": None, "location": "Clinic / Online", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": "dietitian_rachel", "prep": "Bring 3-day food diary", "backup_activities": ["Email food diary for async review"], "skip_adjustments": "Send food diary via email for feedback", "metrics": ["weight", "body_comp", "macro_adherence"], "details": "Review dietary adherence, adjust macros based on progress"},
    {"id": 50, "name": "Sports psychologist session", "type": "Consultation", "frequency": "monthly", "times_per_period": 2, "period": "month", "duration_min": 45, "preferred_time": "15:00", "facilitator": None, "location": "Clinic / Online", "remote_possible": True, "equipment": [], "specialist": "dr_martinez_psych", "allied_health": None, "prep": "Reflect on mental wellness for the week", "backup_activities": ["Journaling exercise"], "skip_adjustments": "Do guided self-reflection exercise", "metrics": ["mood_score", "stress_level", "motivation_score"], "details": "Stress management, performance anxiety, habit formation"},
    {"id": 51, "name": "Dermatologist check-up", "type": "Consultation", "frequency": "monthly", "times_per_period": 1, "period": "month", "duration_min": 30, "preferred_time": "09:00", "facilitator": None, "location": "Clinic", "remote_possible": True, "equipment": [], "specialist": "dr_kim_derm", "allied_health": None, "prep": "Remove nail polish, note any skin changes", "backup_activities": ["Telehealth skin check"], "skip_adjustments": "Reschedule within month", "metrics": ["skin_health_score"], "details": "Skin cancer screening, review skin health, sunscreen adherence"},
    {"id": 52, "name": "Dentist check-up", "type": "Consultation", "frequency": "monthly", "times_per_period": 1, "period": "month", "duration_min": 45, "preferred_time": "09:00", "facilitator": None, "location": "Dental clinic", "remote_possible": False, "equipment": [], "specialist": "dr_chen_dental", "allied_health": None, "prep": "Brush and floss before visit", "backup_activities": [], "skip_adjustments": "Reschedule within 2 weeks", "metrics": ["gum_health", "cavity_status"], "details": "Routine cleaning and oral health assessment"},
    {"id": 53, "name": "Ophthalmologist check-up", "type": "Consultation", "frequency": "monthly", "times_per_period": 1, "period": "month", "duration_min": 30, "preferred_time": "14:00", "facilitator": None, "location": "Eye clinic", "remote_possible": False, "equipment": [], "specialist": "dr_liu_ophth", "allied_health": None, "prep": "Bring current glasses/contacts", "backup_activities": [], "skip_adjustments": "Reschedule within month", "metrics": ["visual_acuity", "eye_pressure"], "details": "Comprehensive eye exam, retinal health check"},
    {"id": 54, "name": "Occupational therapist session", "type": "Consultation", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 45, "preferred_time": "11:00", "facilitator": None, "location": "Clinic / Home", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": "ot_james", "prep": "Note any daily activity difficulties", "backup_activities": ["Phone consultation"], "skip_adjustments": "Do prescribed home adaptations", "metrics": ["functional_score", "ergonomic_compliance"], "details": "Workstation ergonomics, daily activity optimization, wrist health"},
    {"id": 55, "name": "Speech therapist session", "type": "Consultation", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 30, "preferred_time": "13:00", "facilitator": None, "location": "Clinic", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": "speech_therapist_lisa", "prep": "Practice assigned exercises", "backup_activities": ["Home exercise program"], "skip_adjustments": "Do prescribed exercises at home", "metrics": ["voice_quality_score", "swallowing_assessment"], "details": "Voice projection exercises, breathing coordination for speech"},
    {"id": 56, "name": "General practitioner check-up", "type": "Consultation", "frequency": "monthly", "times_per_period": 1, "period": "month", "duration_min": 30, "preferred_time": "10:00", "facilitator": None, "location": "Clinic", "remote_possible": True, "equipment": [], "specialist": "dr_smith_gp", "allied_health": None, "prep": "Bring medication list and health summary", "backup_activities": ["Telehealth GP visit"], "skip_adjustments": "Reschedule within 2 weeks", "metrics": ["weight", "blood_pressure", "general_wellness"], "details": "Overall health review, medication reconciliation, referral management"},

    # Priority 57-70: Additional fitness / wellness
    {"id": 57, "name": "Tai Chi class", "type": "Fitness routine", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 45, "preferred_time": "08:00", "facilitator": "tai_chi_master_chen", "location": "Park / Studio", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": "Wear loose clothing", "backup_activities": ["Tai Chi video at home"], "skip_adjustments": "Practice at home with video", "metrics": ["balance_score", "stress_level", "adherence"], "details": "24-form Yang style, focus on weight shifting and breathing"},
    {"id": 58, "name": "Pilates session", "type": "Fitness routine", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 45, "preferred_time": "09:00", "facilitator": "pilates_instructor_emma", "location": "Studio", "remote_possible": True, "equipment": ["reformer"], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Mat Pilates at home"], "skip_adjustments": "Do mat Pilates at home", "metrics": ["core_strength", "posture_score", "adherence"], "details": "Reformer Pilates focusing on core and spinal alignment"},
    {"id": 59, "name": "Stair climbing", "type": "Fitness routine", "frequency": "daily", "times_per_period": 5, "period": "week", "duration_min": 10, "preferred_time": "12:00", "facilitator": None, "location": "Office / Home", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Step-ups at home"], "skip_adjustments": "Add extra flight throughout day", "metrics": ["flights_climbed", "heart_rate", "adherence"], "details": "Minimum 10 flights per day, use stairs instead of elevator"},
    {"id": 60, "name": "Posture correction exercises", "type": "Fitness routine", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 10, "preferred_time": "14:00", "facilitator": None, "location": "Any", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Wall angels 5 min"], "skip_adjustments": "Do at next desk break", "metrics": ["posture_score", "adherence"], "details": "Chin tucks, chest openers, scapular squeezes. Every 2 hours ideally"},
    {"id": 61, "name": "Outdoor hiking", "type": "Fitness routine", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 90, "preferred_time": "08:00", "facilitator": None, "location": "Outdoors", "remote_possible": False, "equipment": ["hiking_boots", "heart_rate_monitor"], "specialist": None, "allied_health": None, "prep": "Check weather, pack water and snacks", "backup_activities": ["Long park walk", "Treadmill incline walk"], "skip_adjustments": "Do extended outdoor walk", "metrics": ["distance", "elevation_gain", "heart_rate", "duration"], "details": "Moderate trail, 3-5 miles, varied terrain for ankle stability"},
    {"id": 62, "name": "Dance / movement class", "type": "Fitness routine", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 45, "preferred_time": "18:00", "facilitator": "dance_instructor_maria", "location": "Studio", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Dance workout video at home"], "skip_adjustments": "Dance at home to music 20 min", "metrics": ["enjoyment_score", "heart_rate", "adherence"], "details": "Latin dance or contemporary movement for fun cardio and coordination"},
    {"id": 63, "name": "Resistance band workout", "type": "Fitness routine", "frequency": "weekly", "times_per_period": 2, "period": "week", "duration_min": 20, "preferred_time": "07:30", "facilitator": None, "location": "Home / Travel", "remote_possible": True, "equipment": ["resistance_bands"], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Bodyweight exercises"], "skip_adjustments": "Do bodyweight version", "metrics": ["reps", "sets", "adherence"], "details": "Travel-friendly resistance training: pulls, presses, rotations"},
    {"id": 64, "name": "Ankle stability exercises", "type": "Fitness routine", "frequency": "weekly", "times_per_period": 3, "period": "week", "duration_min": 10, "preferred_time": "09:45", "facilitator": None, "location": "Gym / Home", "remote_possible": True, "equipment": ["balance_board"], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Calf raises and ankle circles"], "skip_adjustments": "Add to balance training", "metrics": ["ankle_stability_score", "adherence"], "details": "Ankle circles, calf raises, single-leg balance, band work"},
    {"id": 65, "name": "Jaw / TMJ exercises", "type": "Fitness routine", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "13:00", "facilitator": None, "location": "Any", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": [], "skip_adjustments": "Do at next meal break", "metrics": ["jaw_pain_score", "adherence"], "details": "Gentle jaw stretches, tongue positioning, relaxation exercises"},

    # Priority 66-80: Additional therapy/wellness
    {"id": 66, "name": "Infrared therapy blanket", "type": "Therapy", "frequency": "weekly", "times_per_period": 3, "period": "week", "duration_min": 30, "preferred_time": "20:00", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": ["infrared_blanket"], "specialist": None, "allied_health": None, "prep": "Hydrate before", "backup_activities": ["Warm bath with Epsom salt"], "skip_adjustments": "Take warm bath instead", "metrics": ["relaxation_score", "adherence"], "details": "Medium heat setting, 30 min session for recovery and relaxation"},
    {"id": 67, "name": "Dry brushing", "type": "Therapy", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "06:50", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": ["dry_brush"], "specialist": None, "allied_health": None, "prep": None, "backup_activities": [], "skip_adjustments": "Skip and resume next day", "metrics": ["skin_quality", "adherence"], "details": "Brush towards heart, before morning shower. Lymphatic support"},
    {"id": 68, "name": "Epsom salt bath", "type": "Therapy", "frequency": "weekly", "times_per_period": 2, "period": "week", "duration_min": 20, "preferred_time": "21:00", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": ["bathtub"], "specialist": None, "allied_health": None, "prep": "Run bath, add 2 cups Epsom salt", "backup_activities": ["Magnesium lotion application"], "skip_adjustments": "Apply topical magnesium", "metrics": ["muscle_soreness", "sleep_quality", "adherence"], "details": "2 cups Epsom salt, optional lavender oil, 15-20 min soak"},
    {"id": 69, "name": "Aromatherapy session", "type": "Therapy", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "21:00", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": ["essential_oil_diffuser"], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Apply lavender to pillow"], "skip_adjustments": "Skip", "metrics": ["sleep_quality", "adherence"], "details": "Lavender and chamomile diffuser blend for sleep"},
    {"id": 70, "name": "Contrast therapy (hot-cold shower)", "type": "Therapy", "frequency": "daily", "times_per_period": 5, "period": "week", "duration_min": 10, "preferred_time": "07:00", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Cold shower only 2 min"], "skip_adjustments": "At minimum do 30 sec cold at end of shower", "metrics": ["alertness_score", "adherence"], "details": "3 rounds: 2 min hot, 30 sec cold. End on cold"},

    # Priority 71-85: Monitoring & lab work
    {"id": 71, "name": "Blood pressure monitoring", "type": "Fitness routine", "frequency": "daily", "times_per_period": 14, "period": "week", "duration_min": 5, "preferred_time": "07:00", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": ["blood_pressure_monitor"], "specialist": None, "allied_health": None, "prep": "Sit calmly 5 min before measurement", "backup_activities": [], "skip_adjustments": "Measure at next opportunity", "metrics": ["systolic", "diastolic", "heart_rate"], "details": "Measure twice: morning and evening. Record in health app"},
    {"id": 72, "name": "Blood glucose monitoring", "type": "Fitness routine", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "07:15", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": ["glucose_monitor"], "specialist": None, "allied_health": None, "prep": None, "backup_activities": [], "skip_adjustments": "Check with next meal", "metrics": ["fasting_glucose", "post_meal_glucose"], "details": "Fasting glucose check. Note if CGM is active"},
    {"id": 73, "name": "Weight and body composition check", "type": "Fitness routine", "frequency": "weekly", "times_per_period": 3, "period": "week", "duration_min": 5, "preferred_time": "06:45", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": ["smart_scale"], "specialist": None, "allied_health": None, "prep": "Before eating or drinking, after bathroom", "backup_activities": [], "skip_adjustments": "Check next scheduled day", "metrics": ["weight", "body_fat_pct", "muscle_mass"], "details": "Use smart scale, log trends not individual readings"},
    {"id": 74, "name": "HRV morning check", "type": "Fitness routine", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "06:30", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": ["heart_rate_monitor"], "specialist": None, "allied_health": None, "prep": "Measure before getting out of bed", "backup_activities": [], "skip_adjustments": "Note missed reading", "metrics": ["HRV", "resting_HR", "readiness_score"], "details": "1-min HRV reading using chest strap or Oura ring"},
    {"id": 75, "name": "Sleep quality review", "type": "Fitness routine", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "06:35", "facilitator": None, "location": "Home", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": [], "skip_adjustments": "Review in evening", "metrics": ["sleep_hours", "sleep_score", "REM_pct", "deep_sleep_pct"], "details": "Review Oura/Whoop data, note subjective sleep quality"},
    {"id": 76, "name": "Monthly blood work", "type": "Consultation", "frequency": "monthly", "times_per_period": 1, "period": "month", "duration_min": 30, "preferred_time": "08:00", "facilitator": None, "location": "Lab", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": "12-hour fast, no supplements morning of", "backup_activities": [], "skip_adjustments": "Reschedule within 1 week", "metrics": ["CBC", "CMP", "lipid_panel", "thyroid_panel", "vitamin_levels", "inflammation_markers"], "details": "Comprehensive panel: CBC, CMP, lipids, thyroid, Vit D, B12, CRP, homocysteine"},
    {"id": 77, "name": "Resting metabolic rate test", "type": "Consultation", "frequency": "monthly", "times_per_period": 1, "period": "month", "duration_min": 30, "preferred_time": "08:00", "facilitator": None, "location": "Clinic", "remote_possible": False, "equipment": ["metabolic_cart"], "specialist": None, "allied_health": "dietitian_rachel", "prep": "12-hour fast, no exercise 24h before", "backup_activities": [], "skip_adjustments": "Reschedule within month", "metrics": ["RMR_calories", "fat_oxidation", "carb_oxidation"], "details": "Indirect calorimetry to calibrate nutrition plan"},

    # Priority 78-90: Skin, dental, misc self-care
    {"id": 78, "name": "Skincare routine - morning", "type": "Therapy", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 10, "preferred_time": "07:10", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Sunscreen only"], "skip_adjustments": "At minimum apply sunscreen", "metrics": ["skin_quality", "adherence"], "details": "Cleanser, vitamin C serum, moisturizer, SPF 50"},
    {"id": 79, "name": "Skincare routine - evening", "type": "Therapy", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 10, "preferred_time": "21:45", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Cleanser and moisturizer only"], "skip_adjustments": "At minimum cleanse face", "metrics": ["skin_quality", "adherence"], "details": "Double cleanse, retinol (3x/week), hyaluronic acid, night cream"},
    {"id": 80, "name": "Oral hygiene - morning", "type": "Therapy", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "07:05", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": ["electric_toothbrush"], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Manual toothbrush"], "skip_adjustments": "Do ASAP", "metrics": ["adherence"], "details": "Electric toothbrush 2 min, tongue scraping, mouthwash"},
    {"id": 81, "name": "Oral hygiene - evening", "type": "Therapy", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 10, "preferred_time": "22:00", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": ["electric_toothbrush", "water_flosser"], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Manual brush and floss"], "skip_adjustments": "Do ASAP", "metrics": ["adherence"], "details": "Floss, water flosser, electric toothbrush 2 min, fluoride rinse"},
    {"id": 82, "name": "Sunscreen reapplication", "type": "Therapy", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 2, "preferred_time": "12:00", "facilitator": None, "location": "Any", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Stay in shade", "Wear hat"], "skip_adjustments": "Limit sun exposure", "metrics": ["UV_exposure", "adherence"], "details": "Reapply SPF 50 to exposed areas midday"},
    {"id": 83, "name": "Weekly health metrics review", "type": "Consultation", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 20, "preferred_time": "09:00", "facilitator": None, "location": "Home", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": "Compile weekly data", "backup_activities": ["Quick 5-min check of key metrics"], "skip_adjustments": "Review with next week's data", "metrics": ["weekly_adherence_pct", "trend_analysis"], "details": "Review all tracked metrics, identify trends, adjust goals. Sunday morning"},
    {"id": 84, "name": "Weekly meal planning", "type": "Food consumption", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 30, "preferred_time": "10:00", "facilitator": None, "location": "Home", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Use previous week's meal plan"], "skip_adjustments": "Use default meal plan template", "metrics": ["adherence"], "details": "Plan meals for the week, create grocery list. Sunday"},
    {"id": 85, "name": "Grocery shopping", "type": "Food consumption", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 60, "preferred_time": "11:00", "facilitator": None, "location": "Grocery store", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": "Finalize grocery list from meal plan", "backup_activities": ["Online grocery delivery"], "skip_adjustments": "Order delivery", "metrics": ["adherence"], "details": "Buy fresh produce, proteins, and staples for the week"},
    {"id": 86, "name": "VO2 max test", "type": "Consultation", "frequency": "monthly", "times_per_period": 1, "period": "month", "duration_min": 45, "preferred_time": "08:00", "facilitator": "trainer_mike", "location": "Gym / Clinic", "remote_possible": False, "equipment": ["treadmill", "metabolic_cart", "heart_rate_monitor"], "specialist": None, "allied_health": None, "prep": "No heavy exercise 24h before, light meal 2h before", "backup_activities": ["Cooper run test (field test)"], "skip_adjustments": "Do field test alternative", "metrics": ["VO2max", "lactate_threshold", "max_HR"], "details": "Progressive treadmill test to exhaustion with metabolic cart"},
    {"id": 87, "name": "DEXA scan", "type": "Consultation", "frequency": "monthly", "times_per_period": 1, "period": "month", "duration_min": 30, "preferred_time": "09:00", "facilitator": None, "location": "Clinic", "remote_possible": False, "equipment": ["dexa_scanner"], "specialist": None, "allied_health": None, "prep": "No exercise morning of, consistent hydration", "backup_activities": ["Smart scale body comp measurement"], "skip_adjustments": "Use smart scale as proxy", "metrics": ["body_fat_pct", "lean_mass", "bone_density", "visceral_fat"], "details": "Full body DEXA for body composition and bone density tracking"},
    {"id": 88, "name": "Cognitive training exercises", "type": "Fitness routine", "frequency": "daily", "times_per_period": 5, "period": "week", "duration_min": 15, "preferred_time": "15:00", "facilitator": None, "location": "Any", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Crossword puzzle or Sudoku"], "skip_adjustments": "Do puzzles instead", "metrics": ["cognitive_score", "reaction_time", "adherence"], "details": "BrainHQ or Lumosity exercises: memory, attention, processing speed"},
    {"id": 89, "name": "Social connection activity", "type": "Therapy", "frequency": "weekly", "times_per_period": 2, "period": "week", "duration_min": 60, "preferred_time": "18:00", "facilitator": None, "location": "Various", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Phone call with friend/family"], "skip_adjustments": "Schedule phone/video call", "metrics": ["social_wellbeing_score", "adherence"], "details": "Dinner with friends, group activity, community event. Loneliness prevention"},
    {"id": 90, "name": "Nature exposure / forest bathing", "type": "Therapy", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 30, "preferred_time": "16:00", "facilitator": None, "location": "Outdoors / Park", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Garden time", "Balcony plants care"], "skip_adjustments": "Spend time with indoor plants", "metrics": ["stress_level", "mood_score", "adherence"], "details": "Mindful time in nature, no phone. Park or forest walk"},
    {"id": 91, "name": "Hand and wrist exercises", "type": "Fitness routine", "frequency": "daily", "times_per_period": 5, "period": "week", "duration_min": 5, "preferred_time": "14:30", "facilitator": None, "location": "Any", "remote_possible": True, "equipment": ["grip_strengthener"], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Finger stretches only"], "skip_adjustments": "Do at next desk break", "metrics": ["grip_strength", "wrist_ROM", "adherence"], "details": "Wrist circles, finger stretches, tendon glides. RSI prevention"},
    {"id": 92, "name": "Neck exercises", "type": "Fitness routine", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "14:15", "facilitator": None, "location": "Any", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Gentle neck rolls"], "skip_adjustments": "Do at next break", "metrics": ["neck_pain_score", "ROM", "adherence"], "details": "Neck stretches, isometric holds, levator scapulae stretch"},
    {"id": 93, "name": "Pelvic floor exercises", "type": "Fitness routine", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "12:30", "facilitator": None, "location": "Any", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": [], "skip_adjustments": "Do at next opportunity", "metrics": ["adherence"], "details": "Kegel exercises: 10 reps x 3 sets, 5-sec hold each"},
    {"id": 94, "name": "Cold exposure face immersion", "type": "Therapy", "frequency": "daily", "times_per_period": 5, "period": "week", "duration_min": 5, "preferred_time": "06:55", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": "Fill bowl with cold water and ice", "backup_activities": ["Splash cold water on face"], "skip_adjustments": "Splash cold water on face", "metrics": ["alertness_score", "vagal_tone", "adherence"], "details": "Submerge face in ice water for 15-30 seconds, 3 rounds. Activates dive reflex"},
    {"id": 95, "name": "Foot health exercises", "type": "Fitness routine", "frequency": "daily", "times_per_period": 5, "period": "week", "duration_min": 5, "preferred_time": "21:10", "facilitator": None, "location": "Home", "remote_possible": True, "equipment": ["lacrosse_ball"], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Toe spreads only"], "skip_adjustments": "Do during TV time", "metrics": ["foot_pain_score", "adherence"], "details": "Toe yoga, arch rolls with lacrosse ball, towel scrunches"},
    {"id": 96, "name": "Nasal breathing practice", "type": "Fitness routine", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 5, "preferred_time": "06:20", "facilitator": None, "location": "Home", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": [], "skip_adjustments": "Practice during morning walk", "metrics": ["breath_rate", "adherence"], "details": "Alternate nostril breathing, 5 min. Set intention for nasal breathing during exercise"},
    {"id": 97, "name": "Health journal entry", "type": "Therapy", "frequency": "daily", "times_per_period": 7, "period": "week", "duration_min": 10, "preferred_time": "22:10", "facilitator": None, "location": "Home", "remote_possible": True, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": ["Voice memo health note"], "skip_adjustments": "Do brief voice memo", "metrics": ["subjective_wellbeing", "adherence"], "details": "Log energy, mood, pain, digestion, notable events. 1-10 scales"},
    {"id": 98, "name": "Weekly progress photos", "type": "Fitness routine", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 5, "preferred_time": "07:00", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": "Same lighting, same clothing", "backup_activities": [], "skip_adjustments": "Take at next opportunity", "metrics": ["visual_progress"], "details": "Front, side, back photos. Same conditions each week. Sunday morning"},
    {"id": 99, "name": "Supplement inventory check", "type": "Food consumption", "frequency": "weekly", "times_per_period": 1, "period": "week", "duration_min": 10, "preferred_time": "10:30", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": [], "skip_adjustments": "Do mid-week", "metrics": ["adherence"], "details": "Check supplement levels, reorder if needed. Sunday"},
    {"id": 100, "name": "Emergency first aid kit check", "type": "Therapy", "frequency": "monthly", "times_per_period": 1, "period": "month", "duration_min": 15, "preferred_time": "10:00", "facilitator": None, "location": "Home", "remote_possible": False, "equipment": [], "specialist": None, "allied_health": None, "prep": None, "backup_activities": [], "skip_adjustments": "Do next week", "metrics": ["adherence"], "details": "Check expiry dates, restock supplies, verify AED knowledge"},
]

def generate_action_plan():
    """Return the action plan as a list of dicts."""
    return ACTIVITIES

FACILITATORS = ["trainer_mike", "yoga_instructor_sarah", "tai_chi_master_chen",
                "pilates_instructor_emma", "dance_instructor_maria"]

SPECIALISTS = ["dr_patel_cardio", "dr_wong_endo", "dr_martinez_psych",
               "dr_kim_derm", "dr_chen_dental", "dr_liu_ophth", "dr_smith_gp"]

ALLIED_HEALTH = ["physio_anna", "dietitian_rachel", "massage_therapist_jen",
                  "acupuncturist_lee", "ot_james", "speech_therapist_lisa"]

EQUIPMENT_LIST = [
    "stationary_bike", "squat_rack", "leg_press", "bench_press", "cable_machine",
    "dumbbells", "kettlebells", "rowing_machine", "treadmill", "reformer",
    "yoga_mat", "stability_ball", "foam_roller", "balance_board", "yoga_blocks",
    "resistance_bands", "grip_strengthener", "swim_goggles", "heart_rate_monitor",
    "sauna", "cold_plunge", "red_light_panel", "compression_boots",
    "infrared_blanket", "blood_pressure_monitor", "glucose_monitor", "smart_scale",
    "blue_light_glasses", "electric_toothbrush", "water_flosser",
    "essential_oil_diffuser", "dry_brush", "blender", "shaker_bottle",
    "water_bottle", "kitchen", "bathtub", "massage_table", "acupuncture_needles",
    "therapy_bands", "hiking_boots", "metabolic_cart", "dexa_scanner",
    "lacrosse_ball"
]


def _date_range():
    d = START_DATE
    while d <= END_DATE:
        yield d
        d += timedelta(days=1)


def _random_availability_blocks(base_hours, days_off_per_week=2, variability=True):
    """Generate per-day availability windows.
    Returns {date_str: [(start_time, end_time), ...]}
    """
    schedule = {}
    for d in _date_range():
        dow = d.weekday()  
        if dow in _pick_days_off(d, days_off_per_week):
            schedule[d.strftime("%Y-%m-%d")] = []
            continue
        slots = []
        for (sh, sm), (eh, em) in base_hours:
            if variability and random.random() < 0.1:
                if random.random() < 0.3:
                    continue  
                sh = max(6, sh + random.choice([-1, 1]))
                eh = min(21, eh + random.choice([-1, 1]))
            if sh < eh:
                slots.append((f"{sh:02d}:{sm:02d}", f"{eh:02d}:{em:02d}"))
        schedule[d.strftime("%Y-%m-%d")] = slots
    return schedule


def _pick_days_off(d, n):
    """Deterministically pick days off for a given week."""
    week_seed = d.isocalendar()[1]
    rng = random.Random(week_seed + hash(str(d.month)))
    days = rng.sample(range(7), n)
    return days


def generate_facilitator_schedules():
    facilitator_hours = {
        "trainer_mike": [((8, 0), (12, 0)), ((14, 0), (18, 0))],
        "yoga_instructor_sarah": [((6, 0), (9, 0)), ((17, 0), (20, 0))],
        "tai_chi_master_chen": [((7, 0), (10, 0))],
        "pilates_instructor_emma": [((8, 0), (12, 0))],
        "dance_instructor_maria": [((17, 0), (20, 0))],
    }
    result = {}
    for name, hours in facilitator_hours.items():
        result[name] = _random_availability_blocks(hours, days_off_per_week=2)
    return result


def generate_specialist_schedules():
    specialist_hours = {
        "dr_patel_cardio": [((9, 0), (13, 0)), ((14, 0), (17, 0))],
        "dr_wong_endo": [((8, 0), (12, 0)), ((13, 0), (16, 0))],
        "dr_martinez_psych": [((10, 0), (13, 0)), ((14, 0), (18, 0))],
        "dr_kim_derm": [((9, 0), (12, 0)), ((13, 0), (16, 0))],
        "dr_chen_dental": [((8, 0), (12, 0)), ((13, 0), (17, 0))],
        "dr_liu_ophth": [((9, 0), (13, 0)), ((14, 0), (17, 0))],
        "dr_smith_gp": [((8, 0), (12, 0)), ((14, 0), (18, 0))],
    }
    result = {}
    for name, hours in specialist_hours.items():
        result[name] = _random_availability_blocks(hours, days_off_per_week=2)
    return result


def generate_allied_health_schedules():
    ah_hours = {
        "physio_anna": [((8, 0), (12, 0)), ((13, 0), (17, 0))],
        "dietitian_rachel": [((9, 0), (12, 0)), ((14, 0), (17, 0))],
        "massage_therapist_jen": [((10, 0), (14, 0)), ((15, 0), (19, 0))],
        "acupuncturist_lee": [((9, 0), (13, 0)), ((14, 0), (17, 0))],
        "ot_james": [((8, 0), (12, 0)), ((13, 0), (16, 0))],
        "speech_therapist_lisa": [((9, 0), (12, 0)), ((13, 0), (16, 0))],
    }
    result = {}
    for name, hours in ah_hours.items():
        result[name] = _random_availability_blocks(hours, days_off_per_week=2)
    return result


def generate_equipment_availability():
    """Equipment is generally always available except for maintenance windows."""
    result = {}
    for eq in EQUIPMENT_LIST:
        schedule = {}
        for d in _date_range():
            ds = d.strftime("%Y-%m-%d")
            if random.random() < 0.05:  
                schedule[ds] = []
            else:
                schedule[ds] = [("06:00", "22:00")]
        result[eq] = schedule
    return result


def generate_client_schedule():
    """Client's own schedule - blocks when they're busy with work/personal."""
    schedule = {}
    for d in _date_range():
        ds = d.strftime("%Y-%m-%d")
        dow = d.weekday()
        if dow < 5: 
            available = [
                ("06:00", "08:30"),
                ("12:00", "13:30"),
                ("17:00", "22:30"),
            ]
            if random.random() < 0.2:
                available = [("06:00", "22:30")]
        else: 
            available = [("06:00", "22:30")]

        if random.random() < 0.15:
            available = [(s, e) for s, e in available if s != "17:00"]

        schedule[ds] = available
    return schedule


def generate_travel_plans():
    """Generate travel periods where client is away from home base."""
    travel = []

    trips = [
        {"destination": "New York", "start": "2025-07-14", "end": "2025-07-18",
         "has_gym": True, "has_kitchen": False, "has_pool": False},
        {"destination": "London", "start": "2025-08-04", "end": "2025-08-11",
         "has_gym": True, "has_kitchen": True, "has_pool": True},
        {"destination": "Cabin Retreat", "start": "2025-08-29", "end": "2025-09-01",
         "has_gym": False, "has_kitchen": True, "has_pool": False},
        {"destination": "Tokyo", "start": "2025-09-15", "end": "2025-09-22",
         "has_gym": True, "has_kitchen": False, "has_pool": True},
    ]
    return trips


def save_all_data(output_dir="data"):
    import os
    os.makedirs(output_dir, exist_ok=True)

    action_plan = generate_action_plan()
    with open(os.path.join(output_dir, "action_plan.json"), "w") as f:
        json.dump(action_plan, f, indent=2)

    fac = generate_facilitator_schedules()
    with open(os.path.join(output_dir, "facilitator_schedules.json"), "w") as f:
        json.dump(fac, f, indent=2)

    spec = generate_specialist_schedules()
    with open(os.path.join(output_dir, "specialist_schedules.json"), "w") as f:
        json.dump(spec, f, indent=2)

    ah = generate_allied_health_schedules()
    with open(os.path.join(output_dir, "allied_health_schedules.json"), "w") as f:
        json.dump(ah, f, indent=2)

    eq = generate_equipment_availability()
    with open(os.path.join(output_dir, "equipment_availability.json"), "w") as f:
        json.dump(eq, f, indent=2)

    cs = generate_client_schedule()
    with open(os.path.join(output_dir, "client_schedule.json"), "w") as f:
        json.dump(cs, f, indent=2)

    tp = generate_travel_plans()
    with open(os.path.join(output_dir, "travel_plans.json"), "w") as f:
        json.dump(tp, f, indent=2)

    print(f"Generated {len(action_plan)} activities")
    print(f"Generated schedules for {len(fac)} facilitators, {len(spec)} specialists, {len(ah)} allied health")
    print(f"Generated availability for {len(eq)} equipment types")
    print(f"Generated client schedule for {len(cs)} days")
    print(f"Generated {len(tp)} travel plans")


if __name__ == "__main__":
    save_all_data()