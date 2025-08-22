# eBookVoice AI Frontend - Manual Test Checklist

This checklist verifies all core features are working correctly before production deployment.

## Pre-Test Setup

- [ ] Backend server is running at `http://localhost:5001`
- [ ] Frontend is running with `npm start`
- [ ] Test files ready: `.txt`, `.pdf`, and `.epub` files

## Core Functionality Tests

### 1. Application Launch
- [ ] App loads without errors
- [ ] Header displays "eBookVoice AI" title
- [ ] Dashboard button is visible and functional
- [ ] No console errors on initial load

### 2. Server Health Checks
- [ ] App shows online status when server is running
- [ ] Stop backend server and verify offline notification appears
- [ ] Offline notification shows: "🚨 AI conversion service is currently down..."
- [ ] "Retry Connection" button works and detects server when back online
- [ ] Restart backend and verify app returns to online status

### 3. File Upload
- [ ] "Choose File" button opens file picker
- [ ] Can select .txt files successfully
- [ ] Can select .pdf files successfully  
- [ ] Can select .epub files successfully (if supported)
- [ ] Unsupported file types show appropriate error
- [ ] Upload shows loading spinner and "Processing..." text
- [ ] Success message appears after upload
- [ ] File appears in conversion list immediately

### 4. Voice Selection
- [ ] Voice selector shows available voices
- [ ] Free voices are selectable
- [ ] Premium voices show upgrade message (if free tier)
- [ ] Selected voice is highlighted
- [ ] Voice changes are reflected in uploads

### 5. Progress Tracking
- [ ] New conversions show "pending" status initially
- [ ] Status updates to "processing" with progress percentage
- [ ] Progress bar visually updates as conversion proceeds
- [ ] Current phase text shows conversion steps
- [ ] Status updates automatically without page refresh
- [ ] Completed conversions show "completed" status
- [ ] Failed conversions show "failed" status with error message

### 6. Audio Player Integration
- [ ] Completed conversions show both "Play" and "Download" buttons
- [ ] "Play" button opens audio player overlay
- [ ] Audio player shows correct title
- [ ] Audio loads without errors
- [ ] Play/Pause button functions correctly
- [ ] Progress slider shows current position
- [ ] Can scrub through audio by dragging slider
- [ ] Skip backward (15s) and forward (15s) buttons work
- [ ] Time display shows current time and total duration
- [ ] Close button (✕) closes the player
- [ ] Player overlay covers entire screen with dark background

### 7. Download Functionality
- [ ] "Download" button works for completed conversions
- [ ] Web: Opens download in new tab
- [ ] Mobile: Shows download URL in alert
- [ ] Downloaded file is valid audio format
- [ ] Downloaded file plays correctly in external player

### 8. Dashboard Integration
- [ ] Dashboard button opens dashboard screen
- [ ] Dashboard shows user information
- [ ] Usage statistics display correctly
- [ ] Recent conversions list matches main screen
- [ ] Back button returns to main screen
- [ ] Dashboard refreshes with pull-to-refresh

### 9. Error Handling
- [ ] Network errors show user-friendly messages
- [ ] Upload timeout shows appropriate message
- [ ] Server errors don't crash the app
- [ ] Invalid files show clear rejection messages
- [ ] Failed conversions show error details
- [ ] Audio loading errors show helpful messages

### 10. User Interface
- [ ] Dark theme appears correctly
- [ ] Purple gradient colors display properly
- [ ] Text is readable with good contrast
- [ ] Buttons have hover effects (web)
- [ ] Touch targets are appropriately sized (mobile)
- [ ] Scrolling works smoothly
- [ ] Loading states show appropriate indicators
- [ ] Success/error states have clear visual feedback

### 11. Responsive Design
- [ ] Web: Layout adapts to different screen sizes
- [ ] Web: Audio player is centered and appropriately sized
- [ ] Mobile: All elements fit screen properly
- [ ] Mobile: Touch interactions work correctly
- [ ] Text remains readable at different zoom levels

### 12. Performance
- [ ] App loads quickly (< 5 seconds)
- [ ] File uploads complete in reasonable time
- [ ] Progress polling doesn't cause performance issues
- [ ] Audio playback starts promptly
- [ ] No memory leaks during extended use
- [ ] Smooth animations and transitions

## Test Scenarios

### Scenario 1: Complete Workflow
1. Upload a small .txt file
2. Watch progress tracking until completion
3. Play audio using built-in player
4. Download the audio file
5. Verify all steps work without errors

### Scenario 2: Error Recovery
1. Start a conversion
2. Stop the backend server mid-conversion
3. Verify offline notification appears
4. Restart server
5. Verify app recovers and polling resumes

### Scenario 3: Multiple Conversions
1. Upload 2-3 files in quick succession
2. Verify all show in conversion list
3. Verify progress tracking for all jobs
4. Test playing different audio files
5. Ensure no conflicts or errors

## Browser/Platform Testing

### Web Browsers
- [ ] Chrome: All features work correctly
- [ ] Firefox: All features work correctly  
- [ ] Safari: All features work correctly
- [ ] Edge: All features work correctly

### Mobile (if applicable)
- [ ] iOS: Core features work
- [ ] Android: Core features work

## Production Readiness Checklist

- [ ] All tests above pass ✅
- [ ] No console errors or warnings
- [ ] Build process completes without issues
- [ ] Environment variables configured correctly
- [ ] API URLs point to production backend
- [ ] Audio playback works across all target platforms
- [ ] File upload limits are appropriate
- [ ] Error messages are user-friendly
- [ ] Performance is acceptable under typical load

## Notes

Add any issues found during testing:

```
Date: ___________
Tester: ___________

Issues Found:
- Issue 1: Description and steps to reproduce
- Issue 2: Description and steps to reproduce

Additional Notes:
- Any observations or suggestions
```

---

**Test Completion**: ___/12 sections completed
**Overall Status**: [ ] Ready for Production [ ] Needs Fixes [ ] Major Issues Found