# ICP Definitions — Contact Revival Scorer

## Table of Contents
1. [How to use this file](#how-to-use)
2. [Empuls ICPs](#empuls)
3. [Plum ICPs](#plum)
4. [Loyalife ICPs](#loyalife)
5. [Tier rules](#tier-rules)

---

## How to use this file {#how-to-use}

Read this at Step 5, to set the **ICP tier** that breaks ties within a seniority level.
There is **no numeric score** — only the five tiers in [Tier rules](#tier-rules).

1. Identify the product inferred from CRM (Empuls / Plum / Compass / Loyalife).
2. Identify the contact's geography (India / Southeast Asia / Middle East / US & Europe)
   from the company location in HubSpot. If geography is not set, default to India and
   flag: `Geography not set — India ICP applied as default. Verify with AE.`
3. Match the contact's title against the persona list for that product + geography.
4. Apply the tier from [Tier rules](#tier-rules).

(Compass — sales-incentive automation — shares the Plum buyer functions: Sales, Sales
Ops, Channel, Partnerships, Revenue Ops. Use the Plum lists for Compass and note it.)

---

## Empuls ICPs {#empuls}

Empuls is an employee engagement and rewards platform. The buyer is in HR / People.
Any title outside HR is Wrong Function regardless of seniority.

### India
| Persona | Top Persona |
|---------|-------------|
| CHRO | ★ YES |
| VP HR | No |
| Director HR | No |
| Head of People & Culture | No |
| Head of Employee Experience | ★ YES |
| Head of HR Operations | No |
| Head of Total Rewards | No |
| HR Business Partner Leader | No |

### Southeast Asia
| Persona | Top Persona |
|---------|-------------|
| HR Director | No |
| Head of People & Culture | ★ YES |
| Employee Experience Lead | ★ YES |
| HR Transformation Head | No |
| HR Operations Head | No |
| Talent & Culture Head | No |

### Middle East
| Persona | Top Persona |
|---------|-------------|
| HR Director | No |
| Head of HR | ★ YES |
| Employee Engagement Lead | No |
| Total Rewards Head | No |
| People & Culture Head | ★ YES |

### US & Europe
| Persona | Top Persona |
|---------|-------------|
| VP People | No |
| Chief People Officer | No |
| Director HR | No |
| Head of Total Rewards | No |
| Employee Experience Director | No |
| People Operations Head | No |

---

## Plum ICPs {#plum}

Plum is a B2B rewards and incentives platform for sales, marketing, and partnerships.
The buyer is in Sales, Marketing, Growth, or Partnerships. An HR-only title is Wrong
Function for Plum unless it explicitly references sales incentives or channel rewards.

### India
| Persona | Top Persona |
|---------|-------------|
| Head of Sales | No |
| Sales Operations Head | No |
| Trade Head / Trade Manager | No |
| Channel Sales Head | No |
| Partnerships Head | No |
| Marketing Head | No |
| Growth Head | No |
| Customer Success Head | No |

### Southeast Asia
| Persona | Top Persona |
|---------|-------------|
| Growth Head | No |
| Marketing Director | No |
| Partnerships Head | No |
| Channel Partnerships Head | No |
| Revenue Operations Head | No |

### Middle East
| Persona | Top Persona |
|---------|-------------|
| Marketing Director | No |
| Partnerships Head | No |
| Channel Sales Director | No |
| Business Development Head | No |

### US & Europe
| Persona | Top Persona |
|---------|-------------|
| VP Partnerships | No |
| Head of Growth | No |
| Customer Marketing Head | No |
| Revenue Operations Head | No |
| Channel Partnerships Director | No |

---

## Loyalife ICPs {#loyalife}

Loyalife is a customer loyalty and CRM platform. The buyer is in CRM, Loyalty,
Marketing, or Customer Experience. HR titles are Wrong Function for Loyalife.

### India
| Persona | Top Persona |
|---------|-------------|
| Head of CRM | No |
| Loyalty Program Head | ★ YES |
| Marketing Director | ★ YES |
| Customer Experience Head | No |
| Digital Marketing Head | No |
| Head of Customer Engagement | No |

### Southeast Asia
| Persona | Top Persona |
|---------|-------------|
| Loyalty Program Director | No |
| CRM Head | No |
| Digital Marketing Director | No |
| Customer Experience Head | No |

### Middle East
| Persona | Top Persona |
|---------|-------------|
| Loyalty Head | No |
| Customer Experience Director | No |
| Marketing Director | No |
| CRM Director | No |

### US & Europe
| Persona | Top Persona |
|---------|-------------|
| Director Loyalty Programs | No |
| CRM Director | No |
| VP Marketing | No |
| Customer Engagement Director | No |
| Lifecycle Marketing Head | No |

---

## Tier rules {#tier-rules}

No numeric score. Assign exactly one tier and use it only to break ties within a
seniority level.

| Tier | How to determine |
|------|------------------|
| Exact match — Top Persona ★ | Title matches a ★ YES persona for the correct product + geography. Flag `★ TOP PERSONA`. |
| Exact match | Title matches a listed persona for the correct product + geography. |
| Adjacent | Right function, not listed — one level below a listed persona. |
| Wrong function | A completely different function from any listed persona for this product (Finance, Legal, IT, Admin, etc.). |
| Unknown | Title corrupted, blank, or unparseable. Apply a notes override if the AE has referenced the role anywhere; otherwise flag the gap. |

**Adjacent examples:**
- Empuls: "HR Manager", "People Partner", "Talent Acquisition Head" (HR, not listed).
- Plum / Compass: "Sales Manager", "Brand Manager", "Digital Partnerships Manager".
- Loyalife: "CRM Manager", "Customer Success Lead", "Brand Experience Manager".

**Wrong function examples:**
- Empuls: any Sales, Finance, IT, Legal, Operations title.
- Plum / Compass: any HR, Finance, Legal, IT title (unless it references sales incentives).
- Loyalife: any HR, Sales, or Finance title.
