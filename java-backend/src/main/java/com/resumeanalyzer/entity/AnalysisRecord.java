package com.resumeanalyzer.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import java.time.LocalDateTime;

@Entity
public class AnalysisRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String username;
    private int overallScore;
    private int qualityScore;
    private int experienceScore;
    private int atsScore;

    private LocalDateTime timestamp;

    public AnalysisRecord() {
        this.timestamp = LocalDateTime.now();
    }

    public AnalysisRecord(String username, int overallScore, int qualityScore, int experienceScore, int atsScore) {
        this.username = username;
        this.overallScore = overallScore;
        this.qualityScore = qualityScore;
        this.experienceScore = experienceScore;
        this.atsScore = atsScore;
        this.timestamp = LocalDateTime.now();
    }

    // Getters and Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public int getOverallScore() {
        return overallScore;
    }

    public void setOverallScore(int overallScore) {
        this.overallScore = overallScore;
    }

    public int getQualityScore() {
        return qualityScore;
    }

    public void setQualityScore(int qualityScore) {
        this.qualityScore = qualityScore;
    }

    public int getExperienceScore() {
        return experienceScore;
    }

    public void setExperienceScore(int experienceScore) {
        this.experienceScore = experienceScore;
    }

    public int getAtsScore() {
        return atsScore;
    }

    public void setAtsScore(int atsScore) {
        this.atsScore = atsScore;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }
}
