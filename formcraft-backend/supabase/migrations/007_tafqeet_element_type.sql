-- Migration 007: Add tafqeet to element_type enum
-- Feature: Tafqeet (تفقيط) amount-to-words control

ALTER TYPE element_type ADD VALUE IF NOT EXISTS 'tafqeet';
