# DeployBot Project Tasks

## 🚨 CRITICAL ISSUES - Discovered January 2, 2025

### **HIGH PRIORITY FIXES NEEDED**
- [ ] **FIX: Custom notification windows not displaying** #critical #backend #websocket
  - Backend processes commands but doesn't send proper WebSocket messages to create windows
  - Expected format: `{type: 'notification', event: 'show_custom', data: {notification: {...}}}`
  - Status: No visual notifications appear despite backend success responses

- [ ] **FIX: Task selection system completely broken** #critical #backend #tasks
  - Returns "No tasks found" for all projects despite populated TODO.md files  
  - Tested: My_Awesome_Project (6 tasks), DemoProject (10 tasks) - all fail
  - Status: Zero task suggestions generated

- [ ] **FIX: Snooze functionality not working** #critical #notifications
  - Commands process successfully but notifications don't reappear after delay
  - May require DeployBot restart to load previous fixes
  - Status: Snooze feature completely non-functional

- [ ] **URGENT: End-to-end notification testing** #critical #integration
  - Test complete flow: deploy detection → task selection → notification display → snooze
  - Verify WebSocket message broadcasting from backend to frontend
  - Status: Core DeployBot functionality broken

## Available Tasks
- [ ] Review and update project documentation #writing
- [ ] Check for security vulnerabilities in dependencies #security
- [ ] Optimize backend performance and memory usage #development
- [ ] Update UI components and improve UX #design
- [ ] Write unit tests for new features #testing
- [ ] Plan next sprint and prioritize features #planning
- [ ] Code review: check recent commits #review
- [ ] Update deployment scripts and CI/CD #devops
- [ ] Research new productivity tools and integrations #research
- [ ] Refactor legacy code sections #refactoring

## Completed Tasks
- [x] Set up unified notifications system #development
- [x] Fix monitoring loop for deploy detection #bugfix
- [x] Implement CWD-aware project detection #feature

## Notes
This TODO.md file enables unified notifications with task suggestions during deployments.
Tasks are categorized with tags for better AI-powered selection. 