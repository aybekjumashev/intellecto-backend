# API Documentation

This document provides a detailed specification for all backend API endpoints required for the Intellecto language learning application.

## General Information

-   **Base URL:** `/api`
-   **Authentication:** All endpoints, except for login and register, require a `Bearer Token` in the `Authorization` header.
-   **Standard Success Response:**
    ```json
    {
      "success": true,
      "data": { ... }
    }
    ```
-   **Standard Error Response:**
    ```json
    {
      "success": false,
      "error": {
        "code": "ERROR_CODE",
        "message": "A descriptive error message.",
        "details": { /* (Optional) Field-specific validation errors */ }
      }
    }
    ```

---

## 1. Authentication API

### 1.1. Register
-   **Endpoint:** `POST /api/auth/register`
-   **Description:** Creates a new user account.
-   **Request Body:**
    ```json
    {
      "name": "John Doe",
      "email": "user@example.com",
      "password": "securePassword123"
    }
    ```
-   **Response Success (201):**
    ```json
    {
      "success": true,
      "data": {
        "id": "uuid-123",
        "email": "user@example.com",
        "name": "John Doe",
        "createdAt": "2025-08-10T10:30:00Z"
      }
    }
    ```

### 1.2. Login
-   **Endpoint:** `POST /api/auth/login`
-   **Description:** Authenticates a user and returns access/refresh tokens.
-   **Request Body:**
    ```json
    {
      "email": "user@example.com",
      "password": "securePassword123"
    }
    ```
-   **Response Success (200):**
    ```json
    {
      "success": true,
      "data": {
        "accessToken": "eyJhbGciOiJIUzI1...",
        "refreshToken": "eyJhbGciOiJIUzI1...",
        "user": {
          "id": "uuid-123",
          "email": "user@example.com",
          "name": "John Doe"
        }
      }
    }
    ```

### 1.3. Refresh Token
-   **Endpoint:** `POST /api/auth/refresh-token`
-   **Description:** Issues a new access token using a valid refresh token.
-   **Request Body:**
    ```json
    {
      "refreshToken": "eyJhbGciOiJIUzI1..."
    }
    ```
-   **Response Success (200):**
    ```json
    {
      "success": true,
      "data": {
        "accessToken": "eyJhbGciOiJIUzI1...",
        "refreshToken": "eyJhbGciOiJIUzI1..."
      }
    }
    ```

### 1.4. Logout
-   **Endpoint:** `POST /api/auth/logout`
-   **Description:** Invalidates the user's refresh token.
-   **Request Body:**
    ```json
    {
      "refreshToken": "eyJhbGciOiJIUzI1..."
    }
    ```
-   **Response Success (200):**
    ```json
    {
      "success": true,
      "message": "Successfully logged out"
    }
    ```

---

## 2. User API

### 2.1. Get User Profile
-   **Endpoint:** `GET /api/user/profile`
-   **Description:** Retrieves the profile information for the currently authenticated user.
-   **Response Success (200):**
    ```json
    {
      "success": true,
      "data": {
        "id": "uuid-123",
        "name": "John Doe",
        "username": "johndoe",
        "email": "user@example.com",
        "currentLevel": "A2",
        "totalStars": 47,
        "completedModules": 2,
        "memberSince": "2024-03-15T10:00:00Z"
      }
    }
    ```

### 2.2. Update User Profile
-   **Endpoint:** `PUT /api/user/profile`
-   **Description:** Updates the profile information for the currently authenticated user.
-   **Request Body:**
    ```json
    {
      "name": "Johnathan Doe",
      "username": "john.doe"
    }
    ```
-   **Response Success (200):**
    ```json
    {
      "success": true,
      "data": {
        "id": "uuid-123",
        "name": "Johnathan Doe",
        "username": "john.doe",
        "email": "user@example.com",
        "currentLevel": "A2",
        "totalStars": 47,
        "completedModules": 2,
        "memberSince": "2024-03-15T10:00:00Z"
      }
    }
    ```

### 2.3. Get User Progress and Statistics
-   **Endpoint:** `GET /api/user/progress`
-   **Description:** Retrieves the user's learning progress and statistics.
-   **Response Success (200):**
    ```json
    {
      "success": true,
      "data": {
        "overview": {
          "currentLevel": "A2",
          "totalStars": 47,
          "completedModules": 2,
          "completedTopics": 6
        },
        "statistics": {
          "dayStreak": 7,
          "avgScore": 87,
          "wordsLearned": 156,
          "studyTimeHours": 23
        },
        "skillProgress": [
          { "skill": "Grammar", "progress": 85 },
          { "skill": "Vocabulary", "progress": 92 },
          { "skill": "Listening", "progress": 78 },
          { "skill": "Reading", "progress": 89 }
        ],
        "weeklyActivity": [
          { "day": "Mon", "active": true },
          { "day": "Tue", "active": true },
          { "day": "Wed", "active": true },
          { "day": "Thu", "active": true },
          { "day": "Fri", "active": true },
          { "day": "Sat", "active": false },
          { "day": "Sun", "active": false }
        ],
        "areasForImprovement": [
          {
            "topicId": 2,
            "topicTitle": "Articles (a, an, the)",
            "accuracy": 65,
            "recommendation": "Needs practice"
          },
          {
            "topicId": 5,
            "topicTitle": "Past Simple vs Present Perfect",
            "accuracy": 72,
            "recommendation": "Review recommended"
          }
        ]
      }
    }
    ```

---

## 3. Learning Path API

### 3.1. Get All Modules
-   **Endpoint:** `GET /api/modules`
-   **Description:** Retrieves the list of all learning modules and their associated topics.
-   **Response Success (200):**
    ```json
    {
      "success": true,
      "data": [
        {
          "id": 1,
          "title": "Beginner Basics",
          "status": "completed",
          "finalScore": 85,
          "topics": [
            { "id": 1, "title": "Present Simple", "stars": 3, "status": "completed" },
            { "id": 2, "title": "Articles (a, an, the)", "stars": 2, "status": "completed" },
            { "id": 3, "title": "Basic Vocabulary", "stars": 3, "status": "completed" },
            { "id": 4, "title": "Question Formation", "stars": 2, "status": "completed" }
          ]
        },
        {
          "id": 2,
          "title": "Elementary Progress",
          "status": "active",
          "finalScore": null,
          "topics": [
            { "id": 5, "title": "Past Simple", "stars": 3, "status": "completed" },
            { "id": 6, "title": "Travel Vocabulary", "stars": 2, "status": "completed" },
            { "id": 7, "title": "Prepositions", "stars": 1, "status": "active" },
            { "id": 8, "title": "Future Tense", "stars": 0, "status": "locked" },
            { "id": 9, "title": "Comparatives", "stars": 0, "status": "locked" }
          ]
        },
        {
          "id": 3,
          "title": "Pre-Intermediate Skills",
          "status": "locked",
          "finalScore": null,
          "topics": [
            { "id": 10, "title": "Present Perfect", "stars": 0, "status": "locked" },
            { "id": 11, "title": "Modal Verbs", "stars": 0, "status": "locked" },
            { "id": 12, "title": "Business Vocabulary", "stars": 0, "status": "locked" }
          ]
        }
      ]
    }
    ```

### 3.2. Get Topic Content
-   **Endpoint:** `GET /api/topics/:topicId/content`
-   **Description:** Retrieves the learning content for a specific topic.
-   **Response Success (200):**
    ```json
    {
      "success": true,
      "data": {
        "id": 7,
        "title": "Prepositions of Time and Place",
        "content": {
          "title": "Prepositions of Time and Place",
          "sections": [
            {
              "heading": "Prepositions of Time",
              "text": "• IN: months, years, seasons (in January, in 2023, in summer)\\n• ON: days, dates (on Monday, on March 15th)\\n• AT: specific times (at 3 o'clock, at noon, at night)"
            },
            {
              "heading": "Prepositions of Place",
              "text": "• IN: inside something (in the room, in the car)\\n• ON: on a surface (on the table, on the wall)\\n• AT: specific locations (at home, at school, at the station)"
            }
          ]
        }
      }
    }
    ```

---

## 4. Assessment API

### 4.1. Get Assessment Questions
-   **Endpoint:** `GET /api/assessment`
-   **Description:** Retrieves the questions for the initial level assessment.
-   **Response Success (200):**
    ```json
    {
      "success": true,
      "data": {
        "assessmentId": "assessment-uuid-456",
        "questions": [
          {
            "id": 1,
            "type": "multiple_choice",
            "question": "Choose the correct form: \"I _____ to school every day.\"",
            "options": ["go", "goes", "going", "went"],
            "category": "grammar"
          },
          {
            "id": 2,
            "type": "multiple_choice",
            "question": "What is the past tense of \"eat\"?",
            "options": ["eated", "ate", "eaten", "eating"],
            "category": "grammar"
          }
        ]
      }
    }
    ```

### 4.2. Submit Assessment Answers
-   **Endpoint:** `POST /api/assessment/submit`
-   **Description:** Submits the user's answers for the assessment.
-   **Request Body:**
    ```json
    {
      "assessmentId": "assessment-uuid-456",
      "answers": [
        { "questionId": 1, "answer": 0 },
        { "questionId": 2, "answer": 1 }
      ]
    }
    ```
-   **Response Success (200):**
    ```json
    {
      "success": true,
      "data": {
        "submissionId": "submission-uuid-789"
      }
    }
    ```

### 4.3. Get Assessment Result
-   **Endpoint:** `GET /api/assessment/result/:submissionId`
-   **Description:** Retrieves the result of an assessment. The frontend may need to poll this endpoint.
-   **Response Processing (202):**
    ```json
    {
      "success": true,
      "status": "processing",
      "message": "AI is analyzing your results. Please check back in a moment."
    }
    ```
-   **Response Success (200):**
    ```json
    {
      "success": true,
      "status": "complete",
      "data": {
        "submissionId": "submission-uuid-789",
        "level": "A2",
        "correctCount": 2,
        "totalQuestions": 2,
        "aiAnalysis": "Based on your answers, you have a solid grasp of basic tenses."
      }
    }
    ```

---

## 5. Exercise API

### 5.1. Get Topic Exercises
-   **Endpoint:** `GET /api/topics/:topicId/exercises`
-   **Description:** Retrieves the exercises for a specific topic.
-   **Response Success (200):**
    ```json
    {
      "success": true,
      "data": {
        "topicId": 5,
        "topicTitle": "Past Simple",
        "exercises": [
          {
            "id": 6,
            "type": "fill_in_blank",
            "question": "Complete: \"I _____ to the store yesterday.\"",
            "sentence": "I _____ to the store yesterday.",
            "options": ["go", "went", "going", "goes"]
          },
          {
            "id": 7,
            "type": "multiple_choice",
            "question": "What is the past tense of \"eat\"?",
            "options": ["eated", "ate", "eaten", "eating"]
          },
          {
            "id": 3,
            "type": "sentence_construction",
            "question": "Arrange these words to make a correct sentence:",
            "words": ["always", "coffee", "drinks", "morning", "in", "the", "he"]
          },
          {
            "id": 4,
            "type": "listening",
            "question": "Listen and type what you hear:",
            "audioUrl": "https://example.com/audio/weather_is_beautiful.mp3"
          }
        ]
      }
    }
    ```
-   **Response Not Ready (202):**
    ```json
    {
        "success": true,
        "status": "generating",
        "message": "Exercises for this topic are being prepared by our AI system."
    }
    ```

### 5.2. Submit Exercise Answers
-   **Endpoint:** `POST /api/topics/:topicId/exercises/submit`
-   **Description:** Submits answers for a topic's exercises and gets the result.
-   **Request Body:**
    ```json
    {
      "answers": [
        { "exerciseId": 6, "answer": "went" },
        { "exerciseId": 7, "answer": 1 },
        { "exerciseId": 3, "answer": [6, 0, 2, 1, 4, 5, 3] },
        { "exerciseId": 4, "answer": "The weather is beautiful today." }
      ]
    }
    ```
-   **Response Success (200):**
    ```json
    {
      "success": true,
      "data": {
        "submissionId": "exercise-submission-uuid-111",
        "correctCount": 3,
        "totalQuestions": 4,
        "starsEarned": 2,
        "performanceAnalysis": "You might want to review this topic again to improve your understanding.",
        "results": [
            {
                "exerciseId": 6,
                "isCorrect": true,
                "correctAnswer": "went",
                "explanation": "\"Went\" is the past form of \"go\"."
            },
            {
                "exerciseId": 7,
                "isCorrect": true,
                "correctAnswer": 1,
                "explanation": "\"Ate\" is the irregular past form of \"eat\"."
            },
            {
                "exerciseId": 3,
                "isCorrect": false,
                "correctAnswer": "He always drinks coffee in the morning.",
                "explanation": "The correct word order is Subject-Adverb-Verb."
            },
            {
                "exerciseId": 4,
                "isCorrect": true,
                "correctAnswer": "The weather is beautiful today.",
                "explanation": "Well done!"
            }
        ]
      }
    }
    ```

---

## 6. Payment API

### 6.1. Unlock Module
-   **Endpoint:** `POST /api/modules/:moduleId/unlock`
-   **Description:** Unlocks a locked module for the user.
-   **Request Body:**
    ```json
    {
      "paymentToken": "telegram-payment-token-xyz"
    }
    ```
-   **Response Success (200):**
    ```json
    {
      "success": true,
      "message": "Module unlocked successfully!",
      "data": {
        "moduleId": 3,
        "newStatus": "active"
      }
    }
    ```
-   **Response Error (402 - Payment Required):**
    ```json
    {
        "success": false,
        "error": {
            "code": "PAYMENT_FAILED",
            "message": "Payment failed or was cancelled."
        }
    }
    ```
