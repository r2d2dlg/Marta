
import { NextRequest, NextResponse } from 'next/server';
import { CRMService } from '@/lib/crm';

export async function GET(request: NextRequest) {
  try {
    const entries = await CRMService.getAllSalesFunnelEntries();
    return NextResponse.json(entries);
  } catch (error) {
    console.error('Error fetching sales funnel entries:', error);
    return NextResponse.json(
      { error: 'Failed to fetch sales funnel entries' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const entry = await CRMService.createSalesFunnelEntry(body);
        return NextResponse.json(entry, { status: 201 });
    } catch (error) {
        console.error('Error creating sales funnel entry:', error);
        return NextResponse.json(
            { error: 'Failed to create sales funnel entry' },
            { status: 500 }
        );
    }
}

export async function PUT(request: NextRequest) {
    try {
        const { searchParams } = new URL(request.url);
        const id = searchParams.get('id');
        const body = await request.json();
        if (!id) {
            return NextResponse.json(
                { error: 'ID is required' },
                { status: 400 }
            );
        }
        const entry = await CRMService.updateSalesFunnelEntry(parseInt(id), body);
        return NextResponse.json(entry);
    } catch (error) {
        console.error('Error updating sales funnel entry:', error);
        return NextResponse.json(
            { error: 'Failed to update sales funnel entry' },
            { status: 500 }
        );
    }
}
