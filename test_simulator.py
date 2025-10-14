import json
import time
import uuid
from datetime import datetime, timedelta
from api_manager import APIManager

class TestSimulator:
    def __init__(self):
        self.api_manager = APIManager()
        self.active_tests = {}  # Store active test sessions
    
    def create_test(self, topic, num_questions, difficulty, question_types, duration):
        """Create a new test session"""
        test_id = str(uuid.uuid4())
        
        # Generate questions
        questions_data = self.api_manager.generate_test_questions(
            topic, num_questions, difficulty, question_types
        )
        
        if "error" in questions_data:
            return {"error": questions_data["error"]}
        
        # Create test session
        test_session = {
            "id": test_id,
            "topic": topic,
            "difficulty": difficulty,
            "duration": duration,  # in minutes
            "questions": questions_data.get("questions", []),
            "current_question": 0,
            "answers": {},
            "start_time": None,
            "end_time": None,
            "time_remaining": duration * 60,  # in seconds
            "status": "created"  # created, in_progress, completed
        }
        
        self.active_tests[test_id] = test_session
        
        return {
            "test_id": test_id,
            "num_questions": len(test_session["questions"]),
            "duration": duration
        }
    
    def start_test(self, test_id):
        """Start a test session"""
        if test_id not in self.active_tests:
            return {"error": "Test not found"}
        
        test = self.active_tests[test_id]
        test["status"] = "in_progress"
        test["start_time"] = datetime.now()
        
        return {
            "test_id": test_id,
            "question": test["questions"][0],
            "question_number": 1,
            "total_questions": len(test["questions"]),
            "time_remaining": test["time_remaining"]
        }
    
    def get_next_question(self, test_id):
        """Get the next question in a test"""
        if test_id not in self.active_tests:
            return {"error": "Test not found"}
        
        test = self.active_tests[test_id]
        
        if test["status"] != "in_progress":
            return {"error": "Test is not in progress"}
        
        current = test["current_question"]
        
        if current >= len(test["questions"]) - 1:
            return {"error": "No more questions"}
        
        test["current_question"] += 1
        
        return {
            "question": test["questions"][test["current_question"]],
            "question_number": test["current_question"] + 1,
            "total_questions": len(test["questions"]),
            "time_remaining": test["time_remaining"]
        }
    
    def submit_answer(self, test_id, answer):
        """Submit an answer for the current question"""
        if test_id not in self.active_tests:
            return {"error": "Test not found"}
        
        test = self.active_tests[test_id]
        
        if test["status"] != "in_progress":
            return {"error": "Test is not in progress"}
        
        current = test["current_question"]
        test["answers"][current] = answer
        
        return {"status": "success"}
    
    def complete_test(self, test_id):
        """Complete a test and calculate results"""
        if test_id not in self.active_tests:
            return {"error": "Test not found"}
        
        test = self.active_tests[test_id]
        test["status"] = "completed"
        test["end_time"] = datetime.now()
        
        # Calculate results
        results = self._calculate_results(test)
        
        return results
    
    def _calculate_results(self, test):
        """Calculate test results"""
        questions = test["questions"]
        answers = test["answers"]
        correct_count = 0
        
        detailed_results = []
        
        for i, question in enumerate(questions):
            user_answer = answers.get(i, "")
            correct_answer = question.get("answer", "")
            is_correct = self._compare_answers(user_answer, correct_answer, question.get("type", ""))
            
            if is_correct:
                correct_count += 1
            
            detailed_results.append({
                "question": question.get("question", ""),
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": question.get("explanation", "")
            })
        
        # Calculate time taken
        if test["start_time"] and test["end_time"]:
            time_taken = (test["end_time"] - test["start_time"]).total_seconds()
        else:
            time_taken = (test["duration"] * 60) - test["time_remaining"]
        
        return {
            "test_id": test["id"],
            "topic": test["topic"],
            "difficulty": test["difficulty"],
            "total_questions": len(questions),
            "correct_answers": correct_count,
            "percentage": round((correct_count / len(questions)) * 100, 2),
            "time_taken": round(time_taken, 2),
            "detailed_results": detailed_results
        }
    
    def _compare_answers(self, user_answer, correct_answer, question_type):
        """Compare user answer with correct answer"""
        if question_type.lower() == "multiple choice":
            return user_answer.lower() == correct_answer.lower()
        elif question_type.lower() == "true/false":
            user_bool = user_answer.lower() in ["true", "t", "yes", "y"]
            correct_bool = correct_answer.lower() in ["true", "t", "yes", "y"]
            return user_bool == correct_bool
        else:  # Short answer or other types
            # Simple text comparison - in a real app, you might use more sophisticated matching
            return user_answer.lower().strip() == correct_answer.lower().strip()
    
    def get_test_status(self, test_id):
        """Get the current status of a test"""
        if test_id not in self.active_tests:
            return {"error": "Test not found"}
        
        test = self.active_tests[test_id]
        
        # Update time remaining if test is in progress
        if test["status"] == "in_progress" and test["start_time"]:
            elapsed = (datetime.now() - test["start_time"]).total_seconds()
            test["time_remaining"] = max(0, (test["duration"] * 60) - elapsed)
            
            # Auto-complete if time is up
            if test["time_remaining"] <= 0:
                test["status"] = "completed"
                test["end_time"] = datetime.now()
                return self._calculate_results(test)
        
        return {
            "test_id": test_id,
            "status": test["status"],
            "current_question": test["current_question"] + 1,
            "total_questions": len(test["questions"]),
            "time_remaining": test["time_remaining"]
        }