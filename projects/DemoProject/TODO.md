# DemoProject Tasks

This is an example TODO.md file for the DemoProject. Tasks are tagged with hashtags to help DeployBot understand context and priority.

## Pending Tasks

- [ ] Write script for product video #short #creative #solo
- [ ] Review Firebase rules and security settings #research #backend #long
- [ ] Design mockups for new dashboard feature #creative #short #design
- [ ] Update project documentation with latest changes #writing #long #solo
- [ ] Research competitor pricing strategies #research #long #business
- [ ] Create social media content for launch #writing #short #creative
- [ ] Optimize database queries for better performance #code #backend #long
- [ ] Plan user interview sessions #research #collab #short
- [ ] Write blog post about product journey #writing #long #solo
- [ ] Set up automated testing pipeline #code #backend #long

## Completed Tasks

- [x] Set up initial project structure
- [x] Configure development environment
- [x] Create basic UI wireframes

## Task Tags Reference

### Duration Tags
- `#short` - Tasks that take 15-30 minutes
- `#long` - Tasks that take 1+ hours

### Type Tags
- `#writing` - Content creation, documentation
- `#code` - Programming, development tasks
- `#research` - Investigation, analysis
- `#creative` - Design, creative work
- `#backend` - Server-side, infrastructure (deprioritized during deploys)
- `#design` - UI/UX design work
- `#business` - Business strategy, planning

### Collaboration Tags
- `#solo` - Can be done independently
- `#collab` - Requires collaboration with others

## Notes

DeployBot will automatically suggest tasks from this list when backend deployments are detected. Tasks tagged with `#backend` will be deprioritized during deploy periods to avoid conflicts. 