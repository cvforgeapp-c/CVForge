import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}))
    const { firstName, lastName, email, password, acceptTerms } = body

    if (!acceptTerms) {
      return NextResponse.json(
        { error: 'You must accept the Terms of Service and Privacy Policy.' },
        { status: 400 }
      )
    }

    if (!firstName || !lastName || !email || !password) {
      return NextResponse.json(
        { error: 'All fields are required.' },
        { status: 400 }
      )
    }

    if (password.length < 8) {
      return NextResponse.json(
        { error: 'Password must be at least 8 characters long.' },
        { status: 400 }
      )
    }

    // Return successful response
    return NextResponse.json(
      { success: true, message: 'Account created successfully!' },
      { status: 200 }
    )
  } catch (err) {
    return NextResponse.json(
      { error: 'Server error during account creation. Please try again.' },
      { status: 500 }
    )
  }
}
