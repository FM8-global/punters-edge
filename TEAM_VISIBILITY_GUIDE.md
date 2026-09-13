# Team Visibility & Access Guide for PunterEdge

This guide explains how to share the PunterEdge deployment and development progress with other FM8 staff members.

## 1. GitHub Repository Access

### Share Repository with Team
All development activity, commits, and pull requests are tracked here:
- **Repository**: https://github.com/FM8-global/punters-edge
- **Main Branch**: Contains all approved code
- **Deployment Status**: Check commits and deployments

### Team Member Setup
1. Ask team members to create GitHub accounts (if they don't have one)
2. Invite them to the FM8-global organization:
   - Go to: https://github.com/orgs/FM8-global/people
   - Click "Invite member"
   - Send invites to team members

### What They Can See
- ✅ All code changes and commits
- ✅ Pull requests and code reviews
- ✅ Issues and project tracking
- ✅ Deployment history
- ✅ E2E test results (in Actions)

### GitHub Permissions Levels
- **Read**: View code, commits, PRs (good for viewing team)
- **Write**: Can create branches and PRs (for developers)
- **Admin**: Full access (for project leads)

**Recommended for FM8 staff**: Read access

---

## 2. Live Deployment Access

### Share the Live App URL
Once deployed to Railway, share:
```
App URL: [Get from Railway dashboard]
Admin Email: info@fm8.global
Admin Password: admin123
```

### Add Team Members as Admin Users
In the admin panel:
1. Login as admin (info@fm8.global / admin123)
2. Go to Admin Panel
3. Add team members:
   ```
   Email: team@fm8.global
   Password: [Generate or set custom]
   ```

### Create Read-Only Demo Account
For viewing without admin privileges:
1. Email: demo@fm8.global
2. Set status: Approved User (not admin)
3. Can view all dashboards but cannot make changes

---

## 3. Deployment Status Dashboard

### Create a Status Page
Share deployment and test status with your team:

**Option A: GitHub Actions Status**
```
https://github.com/FM8-global/punters-edge/actions
```
Shows:
- Build status
- Test results
- Deployment status

**Option B: Railway Deployment Status**
```
https://railway.app/project/[project-id]
```
Shows:
- Live app status
- Resource usage
- Recent deployments

**Option C: Manual Status Document**
Keep a shared document updated:
- [ ] Code pushed to GitHub
- [ ] Docker build successful
- [ ] Railway deployment live
- [ ] E2E tests passing
- [ ] Admin access verified
- [ ] Team access granted

---

## 4. Communication Channels

### Email Updates
Send deployment notifications to team:
```
Subject: PunterEdge Deployment Update - [DATE]

Deployment Status: ✅ Live

App URL: https://punters-edge-prod.railway.app
Admin Email: info@fm8.global

Recent Changes:
- Fixed Docker build configuration
- Added comprehensive E2E tests
- Improved API field naming consistency

E2E Test Results:
✓ 10/10 tests passing
✓ No console errors
✓ All dashboard sections working

Team Access:
- GitHub: [link]
- Live App: [link]
- Admin Credentials: [share securely]

Next Steps:
- Review E2E test results
- Test admin panel functionality
- Validate data accuracy
```

### Slack Integration (if available)
Set up GitHub integration:
```
/github subscribe FM8-global/punters-edge
```

This posts:
- New commits
- PR notifications
- Deployment status
- Test results

---

## 5. Secure Credential Sharing

### For Admin Access
**DO NOT** share passwords in plain text via email.

**Secure methods:**
1. **1Password/LastPass**: Shared vault with team
2. **Bitwarden**: Self-hosted or cloud team password manager
3. **GitHub Secrets**: For CI/CD (not for sharing with humans)
4. **In-person**: Tell them verbally or during meeting

**Setup Process:**
1. Create team members as admins in the app
2. Send them a temporary password
3. Ask them to change it on first login
4. Verify they have access

---

## 6. Documentation Sharing

### Share These Documents with Team
- **E2E_TEST_PLAN.md** - What gets tested and when
- **E2E_TESTING_GUIDE.md** - How to run tests yourself
- **DEPLOYMENT_INSTRUCTIONS.md** - How the app was deployed
- **This file** - Team visibility and access
- **README.md** - Project overview

### Create a Team Wiki
Create a shared knowledge base:
- Deployment procedures
- Troubleshooting guide
- Feature documentation
- API endpoints
- Database schema

---

## 7. Team Roles & Access

### Admin (Project Lead)
- GitHub: Write/Admin access
- App: Full admin access
- Can add/remove users
- Can change passwords
- Can view all logs

**Team Members**: You and [other admins]

### Developers
- GitHub: Write access (create branches, PRs)
- App: Approved user access
- Can test features
- Can review code
- Cannot manage users

**Team Members**: [List developers]

### QA/Testers
- GitHub: Read access
- App: Read-only or approved user access
- Can test functionality
- Can report issues
- Cannot modify code

**Team Members**: [List QA staff]

### Viewers/Stakeholders
- GitHub: Read access
- App: Demo account (read-only)
- Can see status
- Can provide feedback
- Cannot access admin features

**Team Members**: [List stakeholders]

---

## 8. Deployment Checklist for Team

When sharing deployment with team, verify:

- [ ] Repository is accessible to team members
- [ ] GitHub branch protection rules configured
- [ ] Live app URL is accessible
- [ ] Admin panel is working
- [ ] Team member accounts created
- [ ] E2E tests are passing
- [ ] Documentation is up-to-date
- [ ] Error logs are being monitored
- [ ] Backup procedures documented
- [ ] Support contact is clear

---

## 9. Regular Updates for Team

### Daily/Weekly Cadence
**Monday Stand-up**
- Deployment status
- Any blockers
- Tests passing?
- Performance metrics

**End of Week**
- Summary of changes
- Any issues found
- Next week's plan

### GitHub Releases
Create a release for each deployment:
```bash
git tag -a v1.0.0 -m "Initial deployment with E2E tests"
git push origin v1.0.0
```

---

## 10. Monitoring & Alerts

### Set Up Notifications
Team members can watch repository:
```
https://github.com/FM8-global/punters-edge
→ Click "Watch"
→ Select notification preferences
```

### Subscribe to Deployments
Get notified when:
- New commits pushed
- Pull requests created
- Deployments complete
- Issues reported

---

## Next Steps

1. **Add team members to GitHub organization**
   - https://github.com/orgs/FM8-global/people

2. **Share live app URL**
   - Get from Railway dashboard
   - Test access

3. **Create admin accounts for team**
   - Login to app
   - Go to Admin Panel
   - Add team members

4. **Send team communication**
   - Share this guide
   - Provide URLs
   - Set expectations

5. **Schedule team demo**
   - Walk through features
   - Show E2E test results
   - Answer questions

---

## Support & Questions

For team members:
- **GitHub Issues**: Create tickets for bugs/features
- **Pull Requests**: Review before merging
- **Email**: Send deployment updates
- **Meetings**: Schedule demos and sync-ups

---

## Checklist: Team Visibility Complete

- [ ] GitHub organization access granted
- [ ] Repository documented and shared
- [ ] Live app URL working and accessible
- [ ] Admin panel tested by team
- [ ] E2E tests verified passing
- [ ] Documentation shared with team
- [ ] Team member roles assigned
- [ ] Communication channels set up
- [ ] Support process documented
- [ ] Monitoring and alerts configured

**Date Completed**: ___________
**Completed By**: ___________
**Next Review**: ___________
