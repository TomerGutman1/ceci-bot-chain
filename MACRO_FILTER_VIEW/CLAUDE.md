# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This is the **Macro Filter View** component - a statistics dashboard for visualizing Israeli government decisions data. It's part of the larger CECI Bot Chain system that provides Hebrew AI-powered answers about Israeli government decisions.

## System Context

This component is a **frontend statistics module** that connects to the main CECI Bot Chain backend. The parent system (`../`) contains:

- **Backend**: Node.js/TypeScript server (port 5001) with bot chain integration
- **Bot Chain**: 7-layer GPT pipeline for processing Hebrew queries about government decisions  
- **Database**: Supabase PostgreSQL with Israeli government decisions data
- **Main Frontend**: React/TypeScript app (port 3001)

**Important**: Always reference the main system's CLAUDE.md at `../CLAUDE.md` for complete architecture details and current status.

## This Component's Mission

Transform the existing decision cards mockup into a **dynamic statistics dashboard** that provides:

- **Analytics UI**: KPI cards, charts, and filtered views of government decisions
- **Hebrew RTL Support**: Right-to-left layout and Hebrew interface
- **Real-time Filtering**: By government, committee, policy area, date ranges
- **No AI Runtime**: Pure data visualization without GPT calls (unlike the main chat system)
- **Mobile-Friendly**: Responsive design for all devices

## Current Integration Status

### ✅ **Completed Tasks (Updated)**
- **Route Configuration**: Component accessible at `/dashboard/statistics`
- **Navigation**: Navbar "📊 לוח מחוונים" button links correctly  
- **Frontend Structure**: All UI components and tabs implemented
- **Integration Plan**: Complete implementation guide created at `INTEGRATION_PLAN.md`

### 🚧 **Next Steps Required**
- **Backend API**: Statistics endpoints need implementation (`/api/statistics/*`)
- **Mock Data Removal**: Replace hardcoded data with real API calls
- **Database Integration**: Connect to existing DataProviderService
- **Performance Testing**: Validate with 50K+ records

### 🔗 **Access Points**
- **Primary**: `http://localhost/dashboard/statistics` (via nginx)
- **Development**: `http://localhost:3001/dashboard/statistics`
- **Alternative**: `http://localhost:8080/dashboard/statistics`

## Key Technical Requirements

### Architecture
- **Frontend Framework**: React 18 + TypeScript + Vite
- **UI Components**: Radix UI + shadcn/ui + Tailwind CSS  
- **Charts**: Recharts for data visualization
- **State Management**: React Query for server state
- **Data Source**: NEW statistics API at `http://localhost:5001/api/statistics/`

### Design Specifications (from SPEC.md)
- **Color Palette**: Blue primary, orange accent, green success (match main system)
- **Layout**: Cards with soft shadows, large radius (2xl)
- **Charts**: Interactive with tooltips and hover effects
- **Accessibility**: Clear text, icons with labels, color-independent
- **Mobile**: Drawer for filters, stacked layout

### Data Integration Strategy
- **Database Schema**: Reference `../bot_chain/LAYERS_SPECS/israeli_government_decisions_DB_SCHEME.md`
- **Existing Service**: Leverage `../server/src/services/dataProviderService.ts`
- **New API Layer**: Create dedicated statistics endpoints (NO AI/GPT costs)
- **Query Optimization**: Direct SQL aggregations, not bot chain

## Development Commands

Since this is a component within the main system, use the parent directory commands:

```bash
# Development (from parent directory)
cd ../
npm run dev                    # Start frontend (port 3001)
cd server && npm run dev       # Start backend (port 5001)

# Build and Test
npm run build                  # Build frontend
npm run lint                   # Lint code
cd server && npm run build     # Build backend

# Docker (full system)
docker-compose up              # Start all services

# Access the dashboard
open http://localhost/dashboard/statistics
```

## File Structure

```
macro_filter_view/
├── CLAUDE.md                  # This file (updated)
├── SPEC.md                    # UX requirements and design spec  
├── INTEGRATION_PLAN.md        # Complete implementation guide
└── [implementation files]     # React components, hooks, utils
```

## Integration Points (Updated)

### Backend APIs to Implement
- `GET /api/statistics/decisions` - Filtered decisions (paginated)
- `GET /api/statistics/overview` - KPI cards data
- `GET /api/statistics/timeline` - Time series charts
- `GET /api/statistics/policy-areas` - Policy distribution
- `GET /api/statistics/committees` - Committee activity stats
- `GET /api/statistics/governments` - Government comparison
- `GET /api/statistics/filter-options` - Dropdown values
- `POST /api/statistics/export` - Data export functionality

### Frontend Integration (Completed)
- ✅ Integrated with main app routing at `../src/App.tsx`
- ✅ Navigation via `../src/components/layout/Navbar.tsx`
- ✅ Reuses UI components from `../src/components/ui/`
- ✅ Follows existing patterns from dashboard components

### Data Models
- Use existing types from `../src/types/`
- Follow database schema from DataProviderService
- Extend with statistics-specific interfaces

## Development Guidelines

### Code Style
- Follow existing TypeScript patterns in parent directory
- Use established component structure from `../src/components/`
- Maintain Hebrew RTL support with existing utilities
- Implement responsive design matching main system

### Performance Requirements
- Target <300ms filter response time (with debouncing)
- Support 50K+ records efficiently
- Use React Query for caching and optimistic updates
- Implement virtual scrolling for large data sets

### Cost Constraints
- **Zero AI/GPT costs** for statistics (unlike chat system)
- Direct database queries only
- Efficient SQL with proper aggregations
- Caching to minimize repeated queries

### URLs and State
- ✅ URL routing configured for `/dashboard/statistics`
- [ ] URL query parameters for shareable filter states
- [ ] Maintain filter state across navigation
- [ ] Support deep linking to specific views

## Testing Strategy

Since the main system has **suspended CI tests due to budget constraints**:
- Focus on manual testing with real data
- Test with existing decision dataset in development
- Validate Hebrew text rendering and RTL layout
- Ensure mobile responsiveness on different devices
- Test concurrent usage with chat system (no interference)

## Budget Considerations

This component should have **zero AI costs** as it's pure data visualization:
- ✅ No bot chain involvement
- ✅ No GPT API calls
- ✅ Direct database access only
- [ ] Implement efficient SQL queries
- [ ] Add caching layer for performance
- [ ] Monitor database query costs

## Implementation Checklist

### ✅ **Phase 1: Frontend Setup (Completed)**
- [x] Update route from `/macro-filter` to `/dashboard/statistics`
- [x] Update navbar navigation
- [x] Verify no conflicts with existing `/decisions` route
- [x] Create comprehensive integration plan

### 🚧 **Phase 2: Backend API (Next Priority)**
- [ ] Create `../server/src/routes/statistics.ts`
- [ ] Create `../server/src/services/statisticsService.ts`
- [ ] Implement all statistics endpoints
- [ ] Add to main router in `../server/src/routes/index.ts`
- [ ] Test with real government decisions data

### 🚧 **Phase 3: Frontend-Backend Connection**
- [ ] Update `src/macro_filter_view/services/api.ts` endpoints
- [ ] Remove mock data from all components
- [ ] Add loading states and error handling
- [ ] Test end-to-end functionality

### 🚧 **Phase 4: Performance & Polish**
- [ ] Optimize database queries
- [ ] Add caching layer
- [ ] Mobile testing and optimization
- [ ] Hebrew UI polish and RTL validation

## Getting Started

1. **Read the integration plan**: Start with `INTEGRATION_PLAN.md` for step-by-step implementation
2. **Study existing backend**: Check `../server/src/services/dataProviderService.ts` for data access patterns
3. **Review database schema**: Understand available data structure
4. **Implement statistics service**: Create backend API layer first
5. **Connect frontend**: Update API calls and remove mock data

## Related Documentation

- `../CLAUDE.md` - Main system architecture and current status
- `../PROJECT_SUMMARY.md` - System overview and service ports  
- `../OPTIMIZATION_PLAN.md` - Performance and cost optimization details
- `../bot_chain/LAYERS_SPECS/israeli_government_decisions_DB_SCHEME.md` - Database schema
- `INTEGRATION_PLAN.md` - Complete implementation guide (THIS FOLDER)

## Work Process Guidelines

1. First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.
2. The plan should have a list of todo items that you can check off as you complete them
3. Before you begin working, check in with me and I will verify the plan.
4. Then, begin working on the todo items, marking them as complete as you go.
5. Please every step of the way just give me a high level explanation of what changes you made
6. Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. Finally, add a review section to the [todo.md](http://todo.md/) file with a summary of the changes you made and any other relevant information.

## Important Reminders

- **Zero Disruption**: Do not modify existing chat/bot chain functionality
- **Cost Control**: No AI/GPT usage for statistics - direct SQL only
- **Simplicity**: Keep changes minimal and focused
- **Integration**: Use existing infrastructure where possible
- **Testing**: Manual testing focus due to budget constraints

