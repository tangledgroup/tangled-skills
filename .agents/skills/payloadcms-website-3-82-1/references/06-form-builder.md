# Form Builder Plugin

This reference covers the Payload Form Builder plugin integration, including form creation, field configuration, submission handlers (email and webhooks), and embedding forms in pages.

## Overview

The template includes `@payloadcms/plugin-form-builder` which provides a visual form builder in the admin panel. Forms can be designed without code, submitted via email or webhook, and embedded on any page using the Form block.

## Plugin Configuration

### Basic Setup

```ts
// src/plugins/index.ts
import { formBuilderPlugin } from '@payloadcms/plugin-form-builder'
import { lexicalEditor } from '@payloadcms/richtext-lexical'
import { FixedToolbarFeature, HeadingFeature } from '@payloadcms/richtext-lexical'

export const plugins: Plugin[] = [
  formBuilderPlugin({
    // Disable payment fields (optional)
    fields: {
      payment: false,
    },
    
    // Override form collection fields
    formOverrides: {
      fields: ({ defaultFields }) => {
        return defaultFields.map((field) => {
          if ('name' in field && field.name === 'confirmationMessage') {
            return {
              ...field,
              editor: lexicalEditor({
                features: ({ rootFeatures }) => {
                  return [
                    ...rootFeatures,
                    FixedToolbarFeature(),
                    HeadingFeature({ enabledHeadingSizes: ['h1', 'h2', 'h3', 'h4'] }),
                  ]
                },
              }),
            }
          }
          return field
        })
      },
    },
  }),
]
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `fields.payment` | boolean | true | Enable payment field types (Stripe) |
| `formOverrides` | object | - | Override Forms collection configuration |
| `submissionOverrides` | object | - | Override Form Submissions collection |

## Creating Forms

### Via Admin Panel

1. Navigate to `/admin` → Collections → Forms
2. Click "New Form"
3. Configure form settings:
   - **Name**: Internal form name (e.g., "Contact Form")
   - **Confirmation Message**: Shown after successful submission
   - **Redirect URL**: Optional URL to redirect after submission
4. Add form fields using the visual builder
5. Configure submission handlers (email/webhook)
6. Save and publish

### Form Fields Available

**Text Input:**

```ts
{
  name: 'name',
  label: 'Full Name',
  type: 'text',
  required: true,
}
```

**Email Input:**

```ts
{
  name: 'email',
  label: 'Email Address',
  type: 'email',
  required: true,
}
```

**Textarea:**

```ts
{
  name: 'message',
  label: 'Your Message',
  type: 'textarea',
  required: true,
  rows: 5,
}
```

**Select Dropdown:**

```ts
{
  name: 'subject',
  label: 'Subject',
  type: 'select',
  required: true,
  choices: [
    { label: 'General Inquiry', value: 'general' },
    { label: 'Support Request', value: 'support' },
    { label: 'Sales Question', value: 'sales' },
  ],
}
```

**Checkbox:**

```ts
{
  name: 'newsletter',
  label: 'Subscribe to newsletter',
  type: 'checkbox',
  required: false,
}
```

**Radio Buttons:**

```ts
{
  name: 'priority',
  label: 'Priority Level',
  type: 'radio',
  required: true,
  choices: [
    { label: 'Low', value: 'low' },
    { label: 'Medium', value: 'medium' },
    { label: 'High', value: 'high' },
  ],
}
```

### Form Structure

**Example Contact Form:**

```json
{
  "name": "Contact Form",
  "confirmationMessage": {
    "root": {
      "type": "root",
      "children": [
        {
          "type": "paragraph",
          "children": [
            { "text": "Thank you for contacting us. We'll get back to you soon!" }
          ]
        }
      ]
    }
  },
  "fields": [
    {
      "name": "name",
      "label": "Full Name",
      "type": "text",
      "required": true,
      "width": 50
    },
    {
      "name": "email",
      "label": "Email Address",
      "type": "email",
      "required": true,
      "width": 50
    },
    {
      "name": "subject",
      "label": "Subject",
      "type": "select",
      "required": true,
      "choices": [
        { "label": "General Inquiry", "value": "general" },
        { "label": "Support Request", "value": "support" }
      ],
      "width": 100
    },
    {
      "name": "message",
      "label": "Your Message",
      "type": "textarea",
      "required": true,
      "rows": 5,
      "width": 100
    }
  ]
}
```

## Submission Handlers

### Email Handler

**Configuration:**

To enable email submissions, configure an email service in Payload:

```ts
// payload.config.ts
import { nodemailerAdapter } from '@payloadcms/email-nodemailer'

export default buildConfig({
  email: nodemailerAdapter({
    defaultFromAddress: 'noreply@your-domain.com',
    defaultFromName: 'Your Website',
    transport: {
      host: process.env.SMTP_HOST,
      port: parseInt(process.env.SMTP_PORT || '587'),
      secure: false,
      auth: {
        user: process.env.SMTP_USER,
        pass: process.env.SMTP_PASS,
      },
    },
  }),
})
```

**Environment Variables:**

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

**Form Email Configuration:**

In the admin panel, add an email action to the form:

```json
{
  "actions": [
    {
      "name": "email",
      "actionType": "email",
      "emailTo": "admin@your-domain.com",
      "emailSubject": "New Form Submission: ${subject}",
      "emailBody": "Name: ${name}\nEmail: ${email}\nSubject: ${subject}\nMessage:\n${message}"
    }
  ]
}
```

**Custom Email Template:**

```ts
// Create custom email rendering
const renderEmailBody = (formData: Record<string, string>): string => {
  return Object.entries(formData)
    .map(([key, value]) => `${key}: ${value}`)
    .join('\n')
}
```

### Webhook Handler

**Configuration:**

Webhooks send form submissions to external URLs:

```json
{
  "actions": [
    {
      "name": "webhook",
      "actionType": "webhook",
      "webhookURL": "https://your-api.com/webhooks/form",
      "customHeaders": {
        "Authorization": "Bearer your-secret-token",
        "Content-Type": "application/json"
      }
    }
  ]
}
```

**Webhook Payload:**

The webhook receives JSON with this structure:

```json
{
  "formID": "form-doc-id-123",
  "formName": "Contact Form",
  "submissionID": "submission-doc-id-456",
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "general",
    "message": "Hello, I have a question..."
  },
  "createdAt": "2024-01-15T10:30:00.000Z"
}
```

### Webhook Handler Example

**Node.js/Express:**

```ts
// server.ts
import express from 'express'

const app = express()
app.use(express.json())

app.post('/webhooks/form', (req, res) => {
  const { formName, data } = req.body
  
  console.log(`Form submission from ${formName}:`, data)
  
  // Process the data
  // - Send to CRM
  // - Create ticket
  // - Store in database
  
  res.json({ received: true })
})

app.listen(3001)
```

**Next.js API Route:**

```ts
// src/app/api/webhooks/form/route.ts
import { NextRequest, NextResponse } from 'next/server'

export async function POST(req: NextRequest) {
  const authHeader = req.headers.get('authorization')
  
  if (authHeader !== `Bearer ${process.env.WEBHOOK_SECRET}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const data = await req.json()
  
  console.log('Form submission received:', data)
  
  // Process the submission
  // - Send email notification
  // - Store in external system
  // - Trigger workflow
  
  return NextResponse.json({ success: true })
}
```

## Embedding Forms in Pages

### Form Block Configuration

**Block Definition:**

```ts
// src/blocks/Form/config.ts
import type { Block } from 'payload'

export const FormBlock: Block = {
  slug: 'formBlock',
  fields: [
    {
      name: 'form',
      type: 'relationship',
      relationTo: 'forms',
      required: true,
      admin: {
        description: 'Select a form to embed on this page',
      },
    },
  ],
}
```

**Adding to Pages Collection:**

```ts
// src/collections/Pages/index.ts
import { FormBlock } from '../../blocks/Form/config'

export const Pages: CollectionConfig<'pages'> = {
  // ...
  fields: [
    {
      type: 'tabs',
      tabs: [
        {
          fields: [
            {
              name: 'layout',
              type: 'blocks',
              blocks: [
                CallToAction,
                Content,
                MediaBlock,
                Archive,
                FormBlock, // Add Form block here
              ],
            },
          ],
          label: 'Content',
        },
      ],
    },
  ],
}
```

### Rendering Forms

**Form Client Component:**

```tsx
// src/blocks/Form/Client.tsx
'use client'

import { useForm } from 'react-hook-form'
import type { Form as FormType } from '@/payload-types'

type FormData = Record<string, string | number | boolean>

export function FormClient({ form }: { form: FormType }) {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>()
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle')

  const onSubmit = async (data: FormData) => {
    setStatus('submitting')
    
    try {
      const res = await fetch('/api/forms/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ formId: form.id, data }),
      })
      
      if (res.ok) {
        setStatus('success')
      } else {
        setStatus('error')
      }
    } catch (error) {
      setStatus('error')
    }
  }

  if (status === 'success') {
    return (
      <div className="p-8 bg-green-50 rounded-lg">
        <h3 className="text-xl font-semibold mb-4">Thank You!</h3>
        <div dangerouslySetInnerHTML={{ __html: form.confirmationMessage }} />
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {form.fields.map((field) => (
        <FormField 
          key={field.name} 
          field={field} 
          register={register}
          errors={errors}
        />
      ))}
      
      {status === 'error' && (
        <div className="p-4 bg-red-50 text-red-700 rounded">
          Something went wrong. Please try again.
        </div>
      )}
      
      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  )
}

// Field renderer component
function FormField({ field, register, errors }: any) {
  const error = errors[field.name]
  
  switch (field.type) {
    case 'text':
    case 'email':
    case 'number':
      return (
        <div>
          <label className="block font-medium mb-2">
            {field.label} {field.required && <span className="text-red-500">*</span>}
          </label>
          <input
            type={field.type}
            {...register(field.name, { required: field.required })}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          {error && <p className="text-red-500 text-sm mt-1">This field is required</p>}
        </div>
      )
    
    case 'textarea':
      return (
        <div>
          <label className="block font-medium mb-2">
            {field.label} {field.required && <span className="text-red-500">*</span>}
          </label>
          <textarea
            {...register(field.name, { required: field.required })}
            rows={field.rows || 4}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          {error && <p className="text-red-500 text-sm mt-1">This field is required</p>}
        </div>
      )
    
    case 'select':
      return (
        <div>
          <label className="block font-medium mb-2">
            {field.label} {field.required && <span className="text-red-500">*</span>}
          </label>
          <select
            {...register(field.name, { required: field.required })}
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select an option</option>
            {field.choices.map((choice: any) => (
              <option key={choice.value} value={choice.value}>
                {choice.label}
              </option>
            ))}
          </select>
          {error && <p className="text-red-500 text-sm mt-1">This field is required</p>}
        </div>
      )
    
    case 'checkbox':
      return (
        <div className="flex items-center">
          <input
            type="checkbox"
            {...register(field.name)}
            className="w-4 h-4"
          />
          <label className="ml-2">{field.label}</label>
        </div>
      )
    
    case 'radio':
      return (
        <div>
          <label className="block font-medium mb-2">
            {field.label} {field.required && <span className="text-red-500">*</span>}
          </label>
          <div className="space-y-2">
            {field.choices.map((choice: any) => (
              <label key={choice.value} className="flex items-center">
                <input
                  type="radio"
                  name={field.name}
                  value={choice.value}
                  {...register(field.name, { required: field.required })}
                  className="mr-2"
                />
                {choice.label}
              </label>
            ))}
          </div>
          {error && <p className="text-red-500 text-sm mt-1">This field is required</p>}
        </div>
      )
    
    default:
      return null
  }
}
```

**Submit API Endpoint:**

```ts
// src/app/api/forms/submit/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { getPayload } from 'payload'
import configPromise from '@payload-config'

export async function POST(req: NextRequest) {
  const payload = await getPayload({ config: configPromise })
  
  const { formId, data } = await req.json()
  
  // Create submission record
  const submission = await payload.create({
    collection: 'form-submissions',
    data: {
      form: formId,
      data,
    },
  })
  
  // Trigger form actions (email, webhook)
  const form = await payload.findByID({
    collection: 'forms',
    id: formId,
    populate: ['fields'],
  })
  
  // Process actions
  if (form.actions) {
    for (const action of form.actions) {
      if (action.actionType === 'email') {
        // Send email
        await payload.sendEmail({
          to: action.emailTo,
          subject: action.emailSubject,
          html: renderEmailBody(data, action.emailBody),
        })
      } else if (action.actionType === 'webhook') {
        // Call webhook
        await fetch(action.webhookURL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...action.customHeaders,
          },
          body: JSON.stringify({
            formID: form.id,
            formName: form.name,
            submissionID: submission.id,
            data,
          }),
        })
      }
    }
  }
  
  return NextResponse.json({ success: true, submissionId: submission.id })
}
```

## Form Submissions Collection

### Viewing Submissions

All form submissions are stored in the `form-submissions` collection:

**Access in Admin Panel:**

1. Navigate to `/admin` → Collections → Form Submissions
2. View all submissions with filtering by form
3. Export submissions as CSV (if configured)

### Querying Submissions

```ts
// Get all submissions for a specific form
const submissions = await payload.find({
  collection: 'form-submissions',
  where: {
    form: { equals: 'form-id-123' },
  },
  sort: '-createdAt',
})

// Get recent submissions across all forms
const recentSubmissions = await payload.find({
  collection: 'form-submissions',
  limit: 50,
  sort: '-createdAt',
})
```

### Submission Data Structure

```ts
{
  id: 'submission-id-456',
  form: {
    relationTo: 'forms',
    value: 'form-id-123',
  },
  data: {
    name: 'John Doe',
    email: 'john@example.com',
    subject: 'general',
    message: 'Hello...',
  },
  createdAt: '2024-01-15T10:30:00.000Z',
  updatedAt: '2024-01-15T10:30:00.000Z',
}
```

## Custom Form Styling

### TailwindCSS Integration

The template uses TailwindCSS for form styling:

```tsx
// Input field with Tailwind classes
<input
  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
  type="text"
  placeholder="Enter your name"
/>

// Button with hover states
<button
  className="w-full bg-blue-600 text-white font-medium py-3 px-6 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition disabled:opacity-50 disabled:cursor-not-allowed"
>
  Submit
</button>

// Form container
<form className="max-w-2xl mx-auto p-8 bg-white rounded-xl shadow-lg space-y-6">
  {/* Form fields */}
</form>
```

### Responsive Layouts

**Two-column layout for narrow fields:**

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
  <FormField field={nameField} />
  <FormField field={emailField} />
</div>
```

## Form Validation

### Client-Side Validation

Using React Hook Form:

```tsx
const { register, handleSubmit, formState: { errors } } = useForm({
  defaultValues: {
    name: '',
    email: '',
    message: '',
  },
})

// Register with validation rules
register('email', {
  required: 'Email is required',
  pattern: {
    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
    message: 'Invalid email address'
  }
})

register('message', {
  required: 'Message is required',
  minLength: {
    value: 10,
    message: 'Message must be at least 10 characters'
  }
})
```

### Server-Side Validation

```ts
// In API route
const validateFormData = (data: FormData): ValidationResult => {
  const errors: Record<string, string> = {}
  
  if (!data.name || data.name.trim().length < 2) {
    errors.name = 'Name must be at least 2 characters'
  }
  
  if (!data.email || !isValidEmail(data.email)) {
    errors.email = 'Valid email is required'
  }
  
  if (!data.message || data.message.trim().length < 10) {
    errors.message = 'Message must be at least 10 characters'
  }
  
  return {
    valid: Object.keys(errors).length === 0,
    errors,
  }
}
```

## Best Practices

### Form Design

1. **Keep forms simple**: Only ask for essential information
2. **Use clear labels**: Be specific about what's needed
3. **Provide examples**: Show format expectations (e.g., email format)
4. **Group related fields**: Organize logically with sections
5. **Show progress**: For multi-step forms, indicate current step

### User Experience

1. **Instant validation**: Show errors as user types
2. **Clear error messages**: Explain what's wrong and how to fix
3. **Success confirmation**: Show clear success message after submission
4. **Loading states**: Disable submit button during processing
5. **Mobile-friendly**: Ensure forms work on all devices

### Security

1. **Validate on server**: Never trust client-side validation alone
2. **Sanitize input**: Prevent XSS and injection attacks
3. **Rate limiting**: Prevent form spam with rate limits
4. **CAPTCHA**: Add reCAPTCHA for public forms if needed
5. **HTTPS only**: Ensure all form submissions use HTTPS

## Troubleshooting

### Forms Not Submitting

**Check:**
- Form ID is correctly set in the block
- API endpoint is accessible
- Required fields are filled
- Network tab for errors

### Email Not Sending

**Check:**
- Email adapter is configured
- SMTP credentials are correct
- Email service allows app passwords
- Check server logs for errors

### Webhook Not Called

**Check:**
- Webhook URL is accessible from server
- Authentication headers are correct
- Webhook endpoint returns 200 OK
- Check webhook service logs

## Next Steps

After implementing forms, explore:
- [Search and Media](07-search-and-media.md) - Full-text search and media management
- [Customizations](08-customizations.md) - Extending with custom functionality
