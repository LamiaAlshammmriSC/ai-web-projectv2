-- ======================================================
--  قاعدة بيانات مشروع محلل المشاعر الذكي
--  استوردها من phpMyAdmin في XAMPP (تبويب Import)
-- ======================================================

CREATE DATABASE IF NOT EXISTS ai_project
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ai_project;

-- جدول نتائج التحليل
CREATE TABLE IF NOT EXISTS analyses (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    text        TEXT NOT NULL,
    sentiment   VARCHAR(20) NOT NULL,          -- positive / negative / neutral
    confidence  DECIMAL(5,2) NOT NULL,         -- نسبة الثقة 0-100
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- جدول بيانات التدريب الإضافية (تصحيحات المستخدم)
-- كل تصحيح يُضاف هنا ويُعاد تدريب النموذج عليه
CREATE TABLE IF NOT EXISTS training_data (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    text        TEXT NOT NULL,
    label       VARCHAR(20) NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
