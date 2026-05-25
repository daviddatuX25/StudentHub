---
phase: 01-code-review
reviewed: 2026-04-13T12:00:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - app/Http/Controllers/ApplicationController.php
  - app/Http/Requests/StoreApplicationRequest.php
  - app/Models/Application.php
  - app/Policies/ApplicationPolicy.php
  - routes/web.php
  - resources/js/Pages/Applications/Apply.svelte
  - resources/js/Pages/Portal/ApplicationEdit.svelte
  - resources/js/Pages/Portal/ApplicationShow.svelte
findings:
  critical: 1
  warning: 3
  info: 4
  total: 8
status: issues_found
---

# Phase 01: Code Review Report

**Reviewed:** 2026-04-13T12:00:00Z
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Reviewed application create/edit feature (Phase 01) for bugs, security vulnerabilities, and code quality issues. Found 1 critical issue, 3 warnings, and 4 info items. The code generally follows Laravel conventions and has proper authorization policies, but there are a few concerns around race conditions in reference number generation, unused code in Svelte components, and minor inconsistencies.

## Critical Issues

### CR-01: Race condition in reference number generation

**File:** `app/Models/Application.php:86-93`
**Issue:** The `nextReferenceNumber()` method has a race condition. It counts existing records with a prefix, then generates a new number. Under concurrent requests, duplicate reference numbers can be generated:

```php
public static function nextReferenceNumber(): string
{
    $year = date('Y');
    $prefix = "APP-{$year}-";
    $count = static::where('reference_number', 'like', $prefix.'%')->count();

    return $prefix.str_pad((string) ($count + 1), 5, '0', STR_PAD_LEFT);
}
```

The gap between `count()` and `create()` allows another request to get the same count.

**Fix:**
```php
public static function nextReferenceNumber(): string
{
    $year = date('Y');
    $prefix = "APP-{$year}-";

    // Use DB lock to prevent race condition
    return DB::transaction(function () use ($prefix) {
        $count = static::where('reference_number', 'like', $prefix.'%')->count();
        return $prefix.str_pad((string) ($count + 1), 5, '0', STR_PAD_LEFT);
    });
}
```

Add `use Illuminate\Support\Facades\DB;` if not already imported.

## Warnings

### WR-01: Unused statuses prop passed to portal edit page

**File:** `ApplicationController.php:747-751`
**Issue:** The `portalEdit` method passes a `statuses` array to the view, but applicants cannot edit the application status anyway. This is unused code.

```php
'statuses' => [
    ['value' => 'pending', 'label' => 'Pending'],
    ['value' => 'accepted', 'label' => 'Accepted'],
    ['value' => 'dismissed', 'label' => 'Dismissed'],
],
```

**Fix:** Remove the statuses prop from the portal edit view since it's not used.

### WR-02: Inconsistent authorization call in storeAdmin

**File:** `ApplicationController.php:194`
**Issue:** The `storeAdmin` method does not explicitly call `$this->authorize()`. While the route is protected by middleware (`role:super_admin,staff,registrar_administrator`), explicit authorization provides defense-in-depth. Compare with `store` (line 367) which also doesn't call authorize but is for public users with application window check.

**Note:** The policy has a `create` method (line 24-27) that checks roles, but it's never invoked in the controller.

**Fix:** Add `$this->authorize('create', Application::class);` at the start of `storeAdmin` or ensure the policy's create method is used.

### WR-03: Potential N+1 in assignedSessionStatus

**File:** `Application.php:99-114`
**Issue:** The `assignedSessionStatus()` method calls `$applicant->examSessions()->get()` which loads all exam sessions. If there could be many sessions per applicant, this could be optimized.

```php
$examSessions = $applicant->examSessions()->get();
if ($examSessions->isEmpty()) {
    return null;
}
return $examSessions->first()?->status;
```

**Fix:** Use `first()` instead of `get()` to fetch only one record:
```php
$examSession = $applicant->examSessions()->first();
return $examSession?->status;
```

## Info

### IN-01: Redundant course filtering logic in Svelte

**File:** `Apply.svelte:32-44` and `ApplicationEdit.svelte:29-41`
**Issue:** The `$derived` and `$derived.by()` blocks deduplicate courses, but the data likely already comes from the database without duplicates. This creates unnecessary computed overhead.

**Note:** This may be defensive if the courses table can have duplicate entries, but if not, this can be simplified.

### IN-02: Unused getAppointments method fallback

**File:** `ApplicationController.php:822`
**Issue:** The `getAppointments()` method returns an empty array if the appointments table doesn't exist. Hardcoded fallback is not provided (unlike `getCourses()` which has defaults).

**Note:** This is acceptable as appointments may not exist in early development, but consider adding defaults like courses for consistency.

### IN-03: Search uses LIKE without input sanitization concern

**File:** `ApplicationController.php:49-54`
**Issue:** The search input uses LIKE queries with user-provided search term. While Laravel uses parameterized queries automatically, the pattern `'%'.$search.'%'` could match unexpected results if the user provides special SQL characters.

**Note:** This is low risk since it's a read-only search, but could consider sanitizing special LIKE characters (%, _) if strict matching is needed.

### IN-04: getCourses defaults hardcoded in controller

**File:** `ApplicationController.php:806-820`
**Issue:** Hardcoded course defaults exist in the controller. This is fine for development, but consider if these should be in configuration or the database instead for production.

**Note:** This is a known pattern in the codebase as shown in other files.

---

_Reviewed: 2026-04-13T12:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_