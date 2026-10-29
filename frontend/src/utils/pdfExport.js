import { jsPDF } from 'jspdf'

export function exportSchemePdf(scheme, eligibility = null, checkedDocs = {}) {
  const doc = new jsPDF()

  const pageWidth = doc.internal.pageSize.getWidth()
  let y = 15

  // Header band
  doc.setFillColor(16, 42, 67) // Navy 900
  doc.rect(0, 0, pageWidth, 28, 'F')

  doc.setTextColor(255, 255, 255)
  doc.setFontSize(18)
  doc.setFont('helvetica', 'bold')
  doc.text('SmartGov AI - Official Scheme Dossier', 14, 14)

  doc.setFontSize(9)
  doc.setFont('helvetica', 'normal')
  doc.text(`Generated on: ${new Date().toLocaleDateString('en-IN')} | www.smartgov.ai`, 14, 22)

  y = 38

  // Scheme Title
  doc.setTextColor(16, 42, 67)
  doc.setFontSize(15)
  doc.setFont('helvetica', 'bold')
  const titleLines = doc.splitTextToSize(scheme.title || 'Scheme Details', pageWidth - 28)
  doc.text(titleLines, 14, y)
  y += titleLines.length * 7 + 2

  // Department & State
  doc.setFontSize(9)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(100, 116, 139)
  const meta = `Department: ${scheme.department || 'N/A'} | State: ${scheme.state || 'All India'} | Category: ${scheme.category || 'General'}`
  doc.text(meta, 14, y)
  y += 8

  // Divider
  doc.setDrawColor(226, 232, 240)
  doc.line(14, y, pageWidth - 14, y)
  y += 6

  // Description
  doc.setFontSize(11)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(16, 42, 67)
  doc.text('1. Scheme Description', 14, y)
  y += 6

  doc.setFontSize(9)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(51, 65, 85)
  const descLines = doc.splitTextToSize(scheme.description || 'No description provided.', pageWidth - 28)
  doc.text(descLines, 14, y)
  y += descLines.length * 5 + 4

  // Key Benefits
  if (scheme.benefits) {
    doc.setFontSize(11)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(15, 122, 92) // Moss
    doc.text('2. Key Benefits & Financial Entitlements', 14, y)
    y += 6

    doc.setFontSize(9)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(51, 65, 85)
    const benLines = doc.splitTextToSize(scheme.benefits, pageWidth - 28)
    doc.text(benLines, 14, y)
    y += benLines.length * 5 + 4
  }

  // Eligibility Evaluation (if available)
  if (eligibility) {
    doc.setFontSize(11)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(16, 42, 67)
    doc.text(`3. Citizen Eligibility Match: ${eligibility.match_score}% (${eligibility.is_eligible ? 'Eligible' : 'Check Criteria'})`, 14, y)
    y += 6

    doc.setFontSize(8.5)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(51, 65, 85)

    if (eligibility.matched_reasons?.length > 0) {
      doc.setTextColor(15, 122, 92)
      doc.text('Matched Criteria:', 16, y)
      y += 4
      doc.setTextColor(51, 65, 85)
      eligibility.matched_reasons.forEach((r) => {
        doc.text(`[YES]  ${r}`, 20, y)
        y += 4.5
      })
      y += 2
    }

    if (eligibility.unmatched_reasons?.length > 0) {
      doc.setTextColor(194, 112, 61)
      doc.text('Unmatched Criteria:', 16, y)
      y += 4
      doc.setTextColor(51, 65, 85)
      eligibility.unmatched_reasons.forEach((r) => {
        doc.text(`[NO]   ${r}`, 20, y)
        y += 4.5
      })
      y += 2
    }
  }

  // Check page height before documents
  if (y > 220) {
    doc.addPage()
    y = 20
  }

  // Required Documents
  if (scheme.documents && scheme.documents.length > 0) {
    doc.setFontSize(11)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(16, 42, 67)
    doc.text('4. Required Documents Checklist', 14, y)
    y += 6

    doc.setFontSize(8.5)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(51, 65, 85)

    scheme.documents.forEach((d) => {
      const isChecked = checkedDocs[d.id] ? '[x] READY' : '[ ] NEEDED'
      const line = `${isChecked}  ${d.document_name} ${d.is_mandatory ? '(*Mandatory)' : '(Optional)'}`
      doc.text(line, 16, y)
      y += 5
    })
    y += 4
  }

  // Check page height before steps
  if (y > 230) {
    doc.addPage()
    y = 20
  }

  // Application Steps
  if (scheme.steps && scheme.steps.length > 0) {
    doc.setFontSize(11)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(16, 42, 67)
    doc.text('5. Step-by-Step How to Apply', 14, y)
    y += 6

    doc.setFontSize(8.5)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(51, 65, 85)

    const sortedSteps = [...scheme.steps].sort((a, b) => a.step_number - b.step_number)
    sortedSteps.forEach((s) => {
      const stepText = `Step ${s.step_number}: ${s.instruction}`
      const stepLines = doc.splitTextToSize(stepText, pageWidth - 32)
      doc.text(stepLines, 16, y)
      y += stepLines.length * 4.5 + 2

      if (y > 275) {
        doc.addPage()
        y = 20
      }
    })
    y += 4
  }

  // Footer on current page
  doc.setFontSize(8)
  doc.setTextColor(148, 163, 184)
  const official = scheme.official_link ? `Official Portal: ${scheme.official_link}` : ''
  doc.text(official, 14, 285)
  doc.text('Verified via SmartGov AI Citizen Portal', pageWidth - 65, 285)

  // Save PDF
  const safeFilename = (scheme.title || 'Scheme')
    .replace(/[^a-zA-Z0-9]/g, '_')
    .slice(0, 30)
  doc.save(`${safeFilename}_Dossier.pdf`)
}
