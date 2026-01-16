# Frontend

## Purpose
The user-facing web application where candidates interact with the mock interview system.

## Structure
```
frontend/
├── public/                 # Static assets (images, fonts, icons)
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── common/        # Buttons, inputs, modals
│   │   ├── interview/     # Interview-specific components
│   │   ├── feedback/      # Results & feedback displays
│   │   └── dashboard/     # User dashboard components
│   ├── pages/             # Page components/routes
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API communication layer
│   ├── store/             # State management (Redux/Zustand)
│   ├── styles/            # Global styles & themes
│   ├── utils/             # Helper functions
│   └── types/             # TypeScript type definitions
├── package.json
└── next.config.js
```

## Key Features
- Video/audio recording interface
- Real-time interview simulation
- Progress dashboard
- Feedback visualization
- Interview history
