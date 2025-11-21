# Cramify Frontend

Next.js frontend for generating AI-powered cheat sheets from lecture PDFs.

## Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Make sure backend is running

The backend should be running on `http://localhost:5000` (Flask API)

## Your Tasks

Complete the TODOs in `app/page.tsx`:

### Task 1: `handleFileChange()`
Handle file selection from the input element.

**What to do:**
- Get files from `event.target.files`
- Convert FileList to array
- Update `selectedFiles` state

### Task 2: `handleGenerate()`
Send files to backend and handle response.

**What to do:**
1. Create FormData object
2. Append files to FormData
3. POST to `/api/generate`
4. Get PDF blob from response
5. Create URL with `URL.createObjectURL()`
6. Update state with PDF URL

## File Structure

```
frontend/
├── app/
│   ├── page.tsx          # Main page (YOUR WORK HERE!)
│   ├── layout.tsx        # App shell (navbar, etc.)
│   └── globals.css       # Global styles
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
├── tailwind.config.ts    # Tailwind CSS config
└── next.config.ts        # Next.js config
```

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [React Hooks (useState)](https://react.dev/reference/react/useState)
- [FormData API](https://developer.mozilla.org/en-US/docs/Web/API/FormData)
- [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
